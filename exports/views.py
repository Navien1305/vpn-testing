from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.decorators import approved_required
from accounts.models import UserRole
from references.models import City, MobileOperator, OperatingSystem, Organization

from .models import ExportLog, ExportStatus, ExportType
from .services import build_excel_export, can_export, get_export_form_choices, parse_export_filters


@approved_required
def export_index(request):
    if not can_export(request.user):
        raise PermissionDenied
    filters = None
    form_choices = {"vpn_forms": [], "messenger_forms": []}
    if request.GET:
        try:
            filters = parse_export_filters(request.GET, request.user)
            form_choices = get_export_form_choices(request.user, filters)
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
    context = {
        "organizations": _organizations_for_user(request.user),
        "cities": City.objects.filter(is_active=True).order_by("name"),
        "mobile_operators": MobileOperator.objects.filter(is_active=True).order_by("name"),
        "os_options": OperatingSystem.choices,
        "filters": request.GET,
        "parsed_filters": filters,
        **form_choices,
    }
    return render(request, "exports/index.html", context)


@approved_required
def export_excel(request):
    if not can_export(request.user):
        raise PermissionDenied
    try:
        filters = parse_export_filters(request.GET, request.user)
        result = build_excel_export(request.user, filters)
        ExportLog.objects.create(
            created_by=request.user,
            export_type=ExportType.EXCEL,
            date_from=filters.date_from,
            date_to=filters.date_to,
            filters_json=filters.as_dict(),
            file_name=result.file_name,
            rows_vpn=result.rows_vpn,
            rows_messenger=result.rows_messenger,
            status=ExportStatus.SUCCESS,
        )
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("export_index")
    except Exception as exc:
        _log_failed_export(request.user, request.GET, exc)
        raise

    response = HttpResponse(
        result.content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{result.file_name}"'
    return response


@approved_required
def export_excel_from_control(request, date_value):
    if not can_export(request.user):
        raise PermissionDenied
    query = request.GET.copy()
    query["date"] = date_value
    export_url = reverse("export_excel")
    return redirect(f"{export_url}?{query.urlencode()}")


def _organizations_for_user(user):
    qs = Organization.objects.filter(is_active=True).order_by("name")
    if user.role == UserRole.COORDINATOR and not user.is_superuser:
        qs = qs.filter(id=user.organization_id)
    return qs


def _log_failed_export(user, params, exc):
    try:
        filters = parse_export_filters(params, user)
        date_from = filters.date_from
        date_to = filters.date_to
        filters_json = filters.as_dict()
    except Exception:
        date_from = None
        date_to = None
        filters_json = dict(params)
    ExportLog.objects.create(
        created_by=user if user.is_authenticated else None,
        export_type=ExportType.EXCEL,
        date_from=date_from,
        date_to=date_to,
        filters_json=filters_json,
        status=ExportStatus.FAILED,
        error_message=str(exc),
    )
