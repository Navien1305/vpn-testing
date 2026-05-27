from datetime import date as date_class

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone

from accounts.decorators import approved_required
from exports.services import can_export

from .services import (
    STATUS_GROUPS,
    apply_plan_filters,
    build_plan_rows,
    can_generate_plan,
    can_view_control,
    filter_context,
    generate_daily_plan,
    group_rows_by_organization,
    plans_for_user,
    split_summary,
)


def _parse_date(date_value):
    try:
        return date_class.fromisoformat(date_value)
    except ValueError as exc:
        raise PermissionDenied("Некорректная дата контроля.") from exc


@approved_required
def control_index(request):
    return redirect("control_detail", date_value=timezone.localdate().isoformat())


@approved_required
def control_detail(request, date_value, status_key=None):
    if not can_view_control(request.user):
        raise PermissionDenied

    control_date = _parse_date(date_value)
    base_qs = plans_for_user(request.user, control_date)
    filtered_qs = apply_plan_filters(base_qs, request.GET)

    selected_status = request.GET.get("status")
    status_filter = None
    if status_key:
        status_filter = STATUS_GROUPS.get(status_key)
    elif selected_status:
        status_filter = [selected_status]

    all_rows = build_plan_rows(base_qs)
    rows = build_plan_rows(filtered_qs, status_filter=status_filter)
    summary = split_summary(all_rows)
    organization_groups = group_rows_by_organization(rows)

    context = {
        "control_date": control_date,
        "plan_count": base_qs.count(),
        "has_plan": base_qs.exists(),
        "organization_groups": organization_groups,
        "summary": summary,
        "can_generate": can_generate_plan(request.user),
        "can_export": can_export(request.user),
        "active_status_key": status_key,
        **filter_context(base_qs, request.GET),
    }
    return render(request, "control/control_detail.html", context)


@approved_required
def control_generate(request, date_value):
    if not can_generate_plan(request.user):
        raise PermissionDenied
    control_date = _parse_date(date_value)
    result = generate_daily_plan(control_date)
    message = f"План сформирован: создано {result.created}, уже существовало {result.existing}."
    if result.skipped:
        message += " Пропущено: " + "; ".join(result.skipped)
    messages.success(request, message)
    return redirect("control_detail", date_value=control_date.isoformat())
