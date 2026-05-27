from dataclasses import dataclass

from django.db.models import QuerySet

from accounts.models import UserRole
from questionnaires.models import MessengerTestForm, VpnFormStatus, VpnTestForm
from references.models import City, MobileOperator, OperatingSystem, Organization, OrganizationType

from .models import DailyFormPlan, DailyFormType


STATUS_MISSING = "missing"
STATUS_PARTIALLY_SUBMITTED = "partially_submitted"

STATUS_LABELS = {
    STATUS_MISSING: "Отсутствует",
    VpnFormStatus.DRAFT: "Черновик",
    VpnFormStatus.SUBMITTED: "Отправлена",
    STATUS_PARTIALLY_SUBMITTED: "Частично отправлена",
    VpnFormStatus.CONFIRMED: "Подтверждена",
    VpnFormStatus.RETURNED: "Возвращена",
}

STATUS_GROUPS = {
    "missing": [STATUS_MISSING],
    "drafts": [VpnFormStatus.DRAFT],
    "submitted": [VpnFormStatus.SUBMITTED, STATUS_PARTIALLY_SUBMITTED],
    "confirmed": [VpnFormStatus.CONFIRMED],
    "returned": [VpnFormStatus.RETURNED],
}


@dataclass
class PlanGenerationResult:
    created: int = 0
    existing: int = 0
    skipped: list[str] | None = None

    def __post_init__(self):
        if self.skipped is None:
            self.skipped = []


def can_view_control(user) -> bool:
    return user.is_authenticated and (
        user.is_superuser or user.role in [UserRole.ADMIN, UserRole.READER, UserRole.COORDINATOR]
    )


def can_generate_plan(user) -> bool:
    return user.is_authenticated and (user.is_superuser or user.role == UserRole.ADMIN)


def generate_daily_plan(date) -> PlanGenerationResult:
    result = PlanGenerationResult()
    cities = list(City.objects.filter(is_active=True).order_by("name"))
    mobile_operators = list(MobileOperator.objects.filter(is_active=True).order_by("name"))
    os_values = [OperatingSystem.ANDROID, OperatingSystem.IOS]

    universities = Organization.objects.filter(
        is_active=True,
        type=OrganizationType.UNIVERSITY,
    ).select_related("city")
    operator_organizations = Organization.objects.filter(
        is_active=True,
        type=OrganizationType.MOBILE_OPERATOR,
        linked_mobile_operator__isnull=False,
    ).select_related("city", "linked_mobile_operator")

    def create_plan(form_type, organization, city, mobile_operator, os_value):
        if not city:
            result.skipped.append(f"{organization}: не указан город")
            return
        plan, created = DailyFormPlan.objects.get_or_create(
            date=date,
            form_type=form_type,
            organization=organization,
            city=city,
            mobile_operator=mobile_operator,
            os=os_value,
            defaults={"expected": True},
        )
        if created:
            result.created += 1
        else:
            result.existing += 1

    for organization in universities:
        for mobile_operator in mobile_operators:
            for os_value in os_values:
                create_plan(DailyFormType.VPN, organization, organization.city, mobile_operator, os_value)
                create_plan(DailyFormType.MESSENGER, organization, organization.city, mobile_operator, os_value)

    for organization in operator_organizations:
        for city in cities:
            for os_value in os_values:
                create_plan(
                    DailyFormType.VPN,
                    organization,
                    city,
                    organization.linked_mobile_operator,
                    os_value,
                )
        for mobile_operator in mobile_operators:
            for os_value in os_values:
                create_plan(DailyFormType.MESSENGER, organization, organization.city, mobile_operator, os_value)

    result.skipped = sorted(set(result.skipped))
    return result


def plans_for_user(user, date) -> QuerySet:
    qs = (
        DailyFormPlan.objects.filter(date=date, expected=True)
        .select_related("organization", "city", "mobile_operator")
        .order_by("form_type", "organization__name", "city__name", "mobile_operator__name", "os")
    )
    if user.role == UserRole.COORDINATOR and not user.is_superuser:
        qs = qs.filter(organization=user.organization)
    return qs


def apply_plan_filters(qs: QuerySet, params):
    if params.get("form_type"):
        qs = qs.filter(form_type=params["form_type"])
    if params.get("organization"):
        qs = qs.filter(organization_id=params["organization"])
    if params.get("city"):
        qs = qs.filter(city_id=params["city"])
    if params.get("mobile_operator"):
        qs = qs.filter(mobile_operator_id=params["mobile_operator"])
    if params.get("os"):
        qs = qs.filter(os=params["os"])
    return qs


def actual_form_for_plan(plan: DailyFormPlan):
    filters = {
        "date": plan.date,
        "organization": plan.organization,
        "city": plan.city,
        "mobile_operator": plan.mobile_operator,
        "os": plan.os,
    }
    if plan.form_type == DailyFormType.VPN:
        return (
            VpnTestForm.objects.filter(**filters)
            .select_related("created_by", "organization", "city", "mobile_operator")
            .first()
        )
    return (
        MessengerTestForm.objects.filter(**filters)
        .select_related("created_by", "organization", "city", "mobile_operator")
        .first()
    )


def build_plan_rows(plans, status_filter=None):
    rows = []
    for plan in plans:
        actual = actual_form_for_plan(plan)
        status = actual.status if actual else STATUS_MISSING
        if status_filter and status not in status_filter:
            continue
        rows.append(
            {
                "plan": plan,
                "actual": actual,
                "status": status,
                "status_label": STATUS_LABELS.get(status, status),
                "tester": getattr(actual, "tester", "") if actual else "",
            }
        )
    return rows


def summarize_rows(rows):
    total = len(rows)
    ready_count = sum(1 for row in rows if row["status"] in [VpnFormStatus.SUBMITTED, VpnFormStatus.CONFIRMED])
    counts = {
        "expected": total,
        "created": sum(1 for row in rows if row["actual"]),
        "missing": sum(1 for row in rows if row["status"] == STATUS_MISSING),
        "draft": sum(1 for row in rows if row["status"] == VpnFormStatus.DRAFT),
        "submitted": sum(1 for row in rows if row["status"] == VpnFormStatus.SUBMITTED),
        "partially_submitted": sum(1 for row in rows if row["status"] == STATUS_PARTIALLY_SUBMITTED),
        "confirmed": sum(1 for row in rows if row["status"] == VpnFormStatus.CONFIRMED),
        "returned": sum(1 for row in rows if row["status"] == VpnFormStatus.RETURNED),
    }
    counts["ready_count"] = ready_count
    counts["percent"] = round((ready_count / total) * 100) if total else 0
    counts["ready"] = total > 0 and ready_count == total
    return counts


def group_rows_by_organization(rows):
    groups_by_id = {}
    for row in rows:
        organization = row["plan"].organization
        group = groups_by_id.setdefault(
            organization.id,
            {
                "organization": organization,
                "rows": [],
            },
        )
        group["rows"].append(row)

    groups = []
    for group in groups_by_id.values():
        group["summary"] = summarize_rows(group["rows"])
        group["vpn_rows"] = [row for row in group["rows"] if row["plan"].form_type == DailyFormType.VPN]
        group["messenger_rows"] = [
            row for row in group["rows"] if row["plan"].form_type == DailyFormType.MESSENGER
        ]
        groups.append(group)
    return sorted(groups, key=lambda item: item["organization"].name)


def split_summary(rows):
    vpn_rows = [row for row in rows if row["plan"].form_type == DailyFormType.VPN]
    messenger_rows = [row for row in rows if row["plan"].form_type == DailyFormType.MESSENGER]
    total = summarize_rows(rows)
    return {
        "total": total,
        "vpn": summarize_rows(vpn_rows),
        "messenger": summarize_rows(messenger_rows),
        "ready_for_export": total["ready"],
    }


def status_choices_for_filter():
    return [
        (STATUS_MISSING, STATUS_LABELS[STATUS_MISSING]),
        (VpnFormStatus.DRAFT, STATUS_LABELS[VpnFormStatus.DRAFT]),
        (STATUS_PARTIALLY_SUBMITTED, STATUS_LABELS[STATUS_PARTIALLY_SUBMITTED]),
        (VpnFormStatus.SUBMITTED, STATUS_LABELS[VpnFormStatus.SUBMITTED]),
    ]


def filter_context(base_qs, params):
    return {
        "filters": params,
        "form_type_choices": DailyFormType.choices,
        "status_choices": status_choices_for_filter(),
        "organizations": base_qs.order_by("organization__name")
        .values_list("organization_id", "organization__name")
        .distinct(),
        "cities": base_qs.order_by("city__name").values_list("city_id", "city__name").distinct(),
        "mobile_operators": base_qs.order_by("mobile_operator__name")
        .values_list("mobile_operator_id", "mobile_operator__name")
        .distinct(),
        "os_options": base_qs.order_by("os").values_list("os", flat=True).distinct(),
    }
