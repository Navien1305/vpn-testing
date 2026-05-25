from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Min
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required

from .forms import CityForm, MessengerForm, MobileOperatorForm, OrganizationForm, VpnAppForm, VpnAppImportForm, VpnAppPeriodForm
from .models import City, Messenger, MobileOperator, OperatingSystem, Organization, VpnApp, VpnAppPeriod
from .services import export_vpn_periods_to_workbook, import_vpn_apps_from_excel


REFERENCE_CONFIG = {
    "organizations": {
        "model": Organization,
        "form": OrganizationForm,
        "list_url": "organization_list",
        "title": "организацию",
    },
    "cities": {
        "model": City,
        "form": CityForm,
        "list_url": "city_list",
        "title": "город",
    },
    "mobile-operators": {
        "model": MobileOperator,
        "form": MobileOperatorForm,
        "list_url": "mobile_operator_list",
        "title": "оператор связи",
    },
    "vpn-apps": {
        "model": VpnAppPeriod,
        "form": VpnAppPeriodForm,
        "list_url": "vpn_app_list",
        "title": "VPN-приложение на период",
    },
    "messengers": {
        "model": Messenger,
        "form": MessengerForm,
        "list_url": "messenger_list",
        "title": "мессенджер",
    },
}


@admin_required
def references_index(request):
    return render(request, "references/index.html")


@admin_required
def organization_list(request):
    organization_ids = (
        Organization.objects.values("name", "type")
        .annotate(first_id=Min("id"))
        .values_list("first_id", flat=True)
    )
    items = Organization.objects.filter(id__in=organization_ids).order_by("type", "name")
    return render(request, "references/organization_list.html", {"items": items})


@admin_required
def city_list(request):
    items = City.objects.order_by("name")
    return render(request, "references/city_list.html", {"items": items})


@admin_required
def mobile_operator_list(request):
    items = MobileOperator.objects.prefetch_related("cities").order_by("name")
    return render(request, "references/mobile_operator_list.html", {"items": items})


@admin_required
def vpn_app_list(request):
    period_options = _vpn_period_options()
    selected_period = request.GET.get("period")
    if not selected_period and period_options:
        selected_period = period_options[0]["value"]

    items = VpnAppPeriod.objects.select_related("vpn_app").order_by("active_from", "display_order", "vpn_app__name")
    if selected_period:
        items = items.filter(_period_query([selected_period]))

    android_items = items.filter(vpn_app__os=OperatingSystem.ANDROID)
    ios_items = items.filter(vpn_app__os=OperatingSystem.IOS)
    return render(
        request,
        "references/vpn_app_list.html",
        {
            "android_items": android_items,
            "ios_items": ios_items,
            "android_count": android_items.count(),
            "ios_count": ios_items.count(),
            "period_options": period_options,
            "selected_period": selected_period,
        },
    )


@admin_required
def vpn_app_import(request):
    if request.method == "POST":
        form = VpnAppImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                result = import_vpn_apps_from_excel(form.cleaned_data["file"])
            except ImportError:
                form.add_error("file", "Не установлен openpyxl. Выполните pip install -r requirements.txt.")
            except Exception as exc:
                form.add_error("file", f"Не удалось прочитать файл: {exc}")
            else:
                period = ""
                if result.active_from and result.active_to:
                    period = f" Период: {result.active_from:%d.%m.%Y} - {result.active_to:%d.%m.%Y}."
                messages.success(
                    request,
                    (
                        "Импорт завершен: "
                        f"создано {result.created}, обновлено {result.updated}, "
                        f"деактивировано {result.deactivated}, пропущено {result.skipped}."
                        f"{period}"
                    ),
                )
                return redirect("vpn_app_list")
    else:
        form = VpnAppImportForm()
    return render(request, "references/vpn_app_import.html", {"form": form})


@admin_required
def messenger_list(request):
    items = Messenger.objects.order_by("display_order", "name")
    return render(request, "references/messenger_list.html", {"items": items})


@admin_required
def vpn_app_delete(request, pk):
    app = get_object_or_404(VpnAppPeriod.objects.select_related("vpn_app"), pk=pk)
    if request.method == "POST":
        app.delete()
        messages.success(request, "VPN-приложение удалено из периода.")
        return redirect("vpn_app_list")
    return render(
        request,
        "references/reference_confirm_delete.html",
        {
            "object": app,
            "title": "Удалить VPN-приложение",
            "back_url": "vpn_app_list",
        },
    )


@admin_required
def vpn_app_export(request):
    selected_periods = request.GET.getlist("period")
    if not selected_periods:
        period_options = _vpn_period_options()
        return render(
            request,
            "references/vpn_app_export.html",
            {"period_options": period_options},
        )

    workbook = export_vpn_periods_to_workbook(selected_periods)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="vpn_periods.xlsx"'
    workbook.save(response)
    return response


@admin_required
def vpn_period_delete(request):
    period_value = request.GET.get("period") or request.POST.get("period")
    if not period_value:
        messages.error(request, "Выберите период для удаления.")
        return redirect("vpn_app_list")

    active_from, active_to = period_value.split("__", 1)
    items = VpnAppPeriod.objects.filter(active_from=active_from, active_to=active_to)
    if request.method == "POST":
        deleted_count, _ = items.delete()
        messages.success(request, f"Период удален. Удалено записей: {deleted_count}.")
        return redirect("vpn_app_list")

    return render(
        request,
        "references/vpn_period_confirm_delete.html",
        {
            "period_value": period_value,
            "period_label": f"{active_from[8:10]}.{active_from[5:7]}.{active_from[0:4]} - {active_to[8:10]}.{active_to[5:7]}.{active_to[0:4]}",
            "items_count": items.count(),
        },
    )


def _vpn_period_options():
    rows = (
        VpnAppPeriod.objects.order_by("-active_from", "-active_to")
        .values("active_from", "active_to")
        .distinct()
    )
    return [
        {
            "value": _period_value(row["active_from"], row["active_to"]),
            "label": f"{row['active_from']:%d.%m.%Y} - {row['active_to']:%d.%m.%Y}",
        }
        for row in rows
    ]


def _period_query(period_values):
    from django.db.models import Q

    query = Q()
    for value in period_values:
        active_from, active_to = value.split("__", 1)
        query |= Q(active_from=active_from, active_to=active_to)
    return query


def _period_value(active_from, active_to):
    return f"{active_from.isoformat()}__{active_to.isoformat()}"


@admin_required
def reference_create(request, reference_type):
    config = REFERENCE_CONFIG[reference_type]
    form_class = config["form"]
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Запись создана.")
            return redirect(config["list_url"])
    else:
        form = form_class()
    return render(
        request,
        "references/reference_form.html",
        {
            "form": form,
            "title": f"Добавить {config['title']}",
            "back_url": config["list_url"],
        },
    )


@admin_required
def reference_update(request, reference_type, pk):
    config = REFERENCE_CONFIG[reference_type]
    obj = get_object_or_404(config["model"], pk=pk)
    form_class = config["form"]
    if request.method == "POST":
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Запись сохранена.")
            return redirect(config["list_url"])
    else:
        form = form_class(instance=obj)
    return render(
        request,
        "references/reference_form.html",
        {
            "form": form,
            "title": f"Редактировать {config['title']}",
            "back_url": config["list_url"],
            "object": obj,
        },
    )
