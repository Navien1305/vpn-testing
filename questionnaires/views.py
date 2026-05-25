from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import approved_required
from accounts.models import UserRole

from .forms import ReturnFormForm, ReturnMeasurementForm, VpnMeasurementBaselineForm, VpnMeasurementResultForm, VpnTestFormCreateForm
from .models import CheckStatus, MeasurementStatus, TesterDevice, VpnFormStatus, VpnMeasurement, VpnTestForm
from .services import (
    available_review_forms,
    can_submit_measurement,
    ensure_measurement_results,
    form_measurement_summary,
    log_action,
    mark_all_results_available,
    measurement_progress,
    ordered_results,
    update_form_status_after_measurement_submit,
)


def _is_admin(user):
    return user.is_superuser or user.role == UserRole.ADMIN


def _can_view_form(user, vpn_form):
    if _is_admin(user) or user.role == UserRole.READER:
        return True
    if user.role == UserRole.COORDINATOR:
        return user.organization_id == vpn_form.organization_id
    return vpn_form.created_by_id == user.id


def _can_edit_form(user, vpn_form):
    if _is_admin(user):
        return True
    if user.role == UserRole.COORDINATOR:
        return user.organization_id == vpn_form.organization_id
    if user.role == UserRole.TESTER:
        return vpn_form.created_by_id == user.id and vpn_form.status in [
            VpnFormStatus.DRAFT,
            VpnFormStatus.RETURNED,
        ]
    return False


def _can_delete_form(user, vpn_form):
    if _is_admin(user):
        return True
    return vpn_form.status == VpnFormStatus.DRAFT and _can_edit_form(user, vpn_form)


def _can_edit_measurement(user, measurement):
    if _is_admin(user):
        return True
    if user.role == UserRole.COORDINATOR:
        return user.organization_id == measurement.form.organization_id
    if user.role == UserRole.TESTER:
        return _can_edit_form(user, measurement.form) and measurement.status in [
            MeasurementStatus.DRAFT,
            MeasurementStatus.RETURNED,
        ]
    return False


def _can_review(user, vpn_form):
    if _is_admin(user):
        return True
    return user.role == UserRole.COORDINATOR and user.organization_id == vpn_form.organization_id


def _sync_form_status_from_measurements(vpn_form, user=None):
    measurements = list(vpn_form.measurements.all())
    if any(measurement.status == MeasurementStatus.RETURNED for measurement in measurements):
        vpn_form.status = VpnFormStatus.RETURNED
        vpn_form.save(update_fields=["status", "updated_at"])
        return
    if measurements and all(measurement.status == MeasurementStatus.CONFIRMED for measurement in measurements):
        vpn_form.status = VpnFormStatus.CONFIRMED
        if user:
            vpn_form.confirmed_by = user
        vpn_form.confirmed_at = timezone.now()
        vpn_form.save(update_fields=["status", "confirmed_by", "confirmed_at", "updated_at"])
        return
    if any(measurement.status == MeasurementStatus.SUBMITTED for measurement in measurements):
        vpn_form.status = VpnFormStatus.SUBMITTED
        vpn_form.save(update_fields=["status", "updated_at"])


def _forms_for_user(user):
    qs = VpnTestForm.objects.select_related("organization", "city", "mobile_operator", "created_by").all()
    if _is_admin(user) or user.role == UserRole.READER:
        return qs
    if user.role == UserRole.COORDINATOR:
        return qs.filter(organization=user.organization)
    return qs.filter(created_by=user)


@approved_required
def vpn_form_list(request):
    forms = _forms_for_user(request.user).order_by("-date", "-created_at")
    deletable_form_ids = {vpn_form.pk for vpn_form in forms if _can_delete_form(request.user, vpn_form)}
    return render(request, "questionnaires/vpn_form_list.html", {"forms": forms, "deletable_form_ids": deletable_form_ids})


@approved_required
def vpn_form_create(request):
    if request.user.role == UserRole.READER:
        raise PermissionDenied
    if not request.user.organization:
        messages.error(request, "У пользователя не указана организация.")
        return redirect("vpn_form_list")
    if request.method == "POST":
        form = VpnTestFormCreateForm(request.POST, user=request.user)
        if form.is_valid():
            vpn_form = form.save(commit=False)
            vpn_form.date = timezone.localdate()
            vpn_form.organization = request.user.organization
            vpn_form.tester = request.user.full_name
            vpn_form.contact = request.user.contact
            vpn_form.created_by = request.user
            vpn_form.device = form.selected_device()
            try:
                vpn_form.save()
            except IntegrityError:
                form.add_error(None, "VPN-анкета с такими параметрами уже существует.")
            else:
                TesterDevice.objects.get_or_create(tester=request.user, name=vpn_form.device)
                messages.success(request, "VPN-анкета создана.")
                return redirect("vpn_form_detail", pk=vpn_form.pk)
    else:
        form = VpnTestFormCreateForm(user=request.user)
    return render(request, "questionnaires/vpn_form_form.html", {"form": form})


@approved_required
def vpn_form_detail(request, pk):
    vpn_form = get_object_or_404(
        VpnTestForm.objects.select_related("organization", "city", "mobile_operator", "created_by").prefetch_related("measurements"),
        pk=pk,
    )
    if not _can_view_form(request.user, vpn_form):
        raise PermissionDenied
    summaries = form_measurement_summary(vpn_form)
    first_measurement = summaries.get(1, {}).get("measurement") if summaries.get(1) else None
    can_start_second = bool(first_measurement and can_submit_measurement(first_measurement))
    return render(
        request,
        "questionnaires/vpn_form_detail.html",
        {
            "vpn_form": vpn_form,
            "summaries": summaries,
            "first_summary": summaries.get(1),
            "second_summary": summaries.get(2),
            "can_start_second": can_start_second,
            "can_edit": _can_edit_form(request.user, vpn_form),
            "can_review": _can_review(request.user, vpn_form),
            "can_review_actions": False,
            "can_read_only": request.user.role == UserRole.READER,
            "can_delete_form": _can_delete_form(request.user, vpn_form),
        },
    )


@approved_required
def vpn_form_delete(request, pk):
    vpn_form = get_object_or_404(VpnTestForm, pk=pk)
    if not _can_delete_form(request.user, vpn_form):
        raise PermissionDenied
    if request.method == "POST":
        vpn_form.delete()
        messages.warning(request, "VPN-анкета удалена.")
        return redirect("vpn_form_list")
    return render(request, "questionnaires/vpn_form_confirm_delete.html", {"vpn_form": vpn_form})


@approved_required
def vpn_measurement_start(request, pk, number):
    vpn_form = get_object_or_404(VpnTestForm, pk=pk)
    if not _can_edit_form(request.user, vpn_form):
        raise PermissionDenied
    if number == 2 and not vpn_form.measurements.filter(
        measurement_number=1,
        status__in=[MeasurementStatus.SUBMITTED, MeasurementStatus.CONFIRMED],
    ).exists():
        messages.warning(request, "Второе тестирование доступно после отправки первого замера на согласование.")
        return redirect("vpn_form_detail", pk=vpn_form.pk)
    measurement, _ = VpnMeasurement.objects.get_or_create(form=vpn_form, measurement_number=number)
    if not _can_edit_measurement(request.user, measurement):
        raise PermissionDenied
    ensure_measurement_results(measurement)
    results = ordered_results(measurement)
    if not results:
        messages.error(request, "Для выбранной даты и ОС нет активных VPN-приложений.")
        return redirect("vpn_form_detail", pk=vpn_form.pk)
    if not measurement.onelostbox_without_vpn_status:
        return redirect("vpn_measurement_baseline", pk=measurement.pk)
    if measurement.status == MeasurementStatus.RETURNED:
        return redirect("vpn_measurement_summary", pk=measurement.pk)
    first_empty_result = next((result for result in results if not result.is_filled), None)
    if first_empty_result:
        return redirect("vpn_measurement_fill", pk=measurement.pk, result_id=first_empty_result.pk)
    return redirect("vpn_measurement_complete", pk=measurement.pk)


@approved_required
def vpn_measurement_baseline(request, pk):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    if not _can_edit_measurement(request.user, measurement):
        raise PermissionDenied
    if request.method == "POST":
        form = VpnMeasurementBaselineForm(request.POST, instance=measurement)
        if form.is_valid():
            measurement = form.save()
            results = ordered_results(measurement)
            if measurement.onelostbox_without_vpn_status == "works":
                mark_all_results_available(measurement)
                return redirect("vpn_measurement_complete", pk=measurement.pk)
            if results:
                return redirect("vpn_measurement_fill", pk=measurement.pk, result_id=results[0].pk)
            return redirect("vpn_measurement_complete", pk=measurement.pk)
    else:
        form = VpnMeasurementBaselineForm(instance=measurement)
    return render(request, "questionnaires/vpn_measurement_baseline.html", {"measurement": measurement, "form": form})


@approved_required
def vpn_measurement_fill(request, pk, result_id):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    vpn_form = measurement.form
    if not _can_edit_measurement(request.user, measurement):
        raise PermissionDenied
    results = ordered_results(measurement)
    result = get_object_or_404(measurement.results.select_related("vpn_app"), pk=result_id)
    index = [item.pk for item in results].index(result.pk)
    next_url = request.POST.get("next") or request.GET.get("next")
    is_summary_edit = next_url == "summary"

    if request.method == "POST":
        form = VpnMeasurementResultForm(request.POST, instance=result)
        if form.is_valid():
            result = form.save(commit=False)
            if result.vpn_unable_to_check:
                result.web_with_vpn_status = CheckStatus.NOT_APPLICABLE
                result.instagram_status = CheckStatus.NOT_APPLICABLE
                result.youtube_status = CheckStatus.NOT_APPLICABLE
            elif result.web_with_vpn_status == CheckStatus.WORKS:
                result.instagram_status = CheckStatus.WORKS
                result.youtube_status = CheckStatus.WORKS
            result.save()
            action = request.POST.get("action")
            if is_summary_edit:
                messages.success(request, "Результат сохранен.")
                return redirect("vpn_measurement_summary", pk=measurement.pk)
            if action == "previous" and index > 0:
                return redirect("vpn_measurement_fill", pk=measurement.pk, result_id=results[index - 1].pk)
            if action == "save":
                messages.success(request, "Результат сохранен.")
                return redirect("vpn_measurement_fill", pk=measurement.pk, result_id=result.pk)
            if index + 1 < len(results):
                return redirect("vpn_measurement_fill", pk=measurement.pk, result_id=results[index + 1].pk)
            return redirect("vpn_measurement_complete", pk=measurement.pk)
    else:
        form = VpnMeasurementResultForm(instance=result)

    return render(
        request,
        "questionnaires/vpn_measurement_fill.html",
        {
            "measurement": measurement,
            "result": result,
            "form": form,
            "index": index + 1,
            "total": len(results),
            "previous_result": results[index - 1] if index > 0 else None,
            "next_result": results[index + 1] if index + 1 < len(results) else None,
            "next_url": next_url,
            "is_summary_edit": is_summary_edit,
        },
    )


@approved_required
def vpn_measurement_complete(request, pk):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    if not _can_view_form(request.user, measurement.form):
        raise PermissionDenied
    progress = measurement_progress(measurement)
    return render(
        request,
        "questionnaires/vpn_measurement_complete.html",
        {
            "measurement": measurement,
            "progress": progress,
            "can_submit": request.user.role == UserRole.TESTER and _can_edit_measurement(request.user, measurement) and can_submit_measurement(measurement),
        },
    )


@approved_required
def vpn_measurement_summary(request, pk):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    if not _can_view_form(request.user, measurement.form):
        raise PermissionDenied
    results = ordered_results(measurement)
    progress = measurement_progress(measurement)
    return render(
        request,
        "questionnaires/vpn_measurement_summary.html",
        {
            "measurement": measurement,
            "results": results,
            "progress": progress,
            "can_edit_measurement": _can_edit_measurement(request.user, measurement),
            "can_submit": request.user.role == UserRole.TESTER and _can_edit_measurement(request.user, measurement) and can_submit_measurement(measurement),
            "can_review_measurement_actions": _can_review(request.user, measurement.form) and measurement.status == MeasurementStatus.SUBMITTED,
        },
    )


@approved_required
def vpn_measurement_submit(request, pk):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    if not _can_edit_measurement(request.user, measurement):
        raise PermissionDenied
    if not can_submit_measurement(measurement):
        messages.error(request, "Нельзя отправить замер: заполнены не все VPN или отсутствует обязательный комментарий.")
        return redirect("vpn_measurement_complete", pk=measurement.pk)
    measurement.status = MeasurementStatus.SUBMITTED
    measurement.submitted_at = timezone.now()
    measurement.confirmed_at = None
    measurement.returned_at = None
    measurement.return_comment = ""
    measurement.checked_by = None
    measurement.save(update_fields=["status", "submitted_at", "confirmed_at", "returned_at", "return_comment", "checked_by", "updated_at"])
    update_form_status_after_measurement_submit(measurement.form)
    log_action("vpn_measurement_submitted", request.user, measurement)
    messages.success(request, "Анкета отправлена куратору.")
    return redirect("vpn_form_detail", pk=measurement.form_id)


@approved_required
def vpn_form_submit_single_measurement(request, pk):
    vpn_form = get_object_or_404(VpnTestForm, pk=pk)
    if not _can_edit_form(request.user, vpn_form):
        raise PermissionDenied
    first = vpn_form.measurements.filter(measurement_number=1, status__in=[MeasurementStatus.SUBMITTED, MeasurementStatus.CONFIRMED]).first()
    if not first:
        messages.error(request, "Сначала отправьте первый замер на проверку.")
        return redirect("vpn_form_detail", pk=vpn_form.pk)
    vpn_form.status = VpnFormStatus.SUBMITTED
    vpn_form.submitted_at = timezone.now()
    vpn_form.save(update_fields=["status", "submitted_at", "updated_at"])
    messages.success(request, "Анкета завершена только с первым замером и отправлена на проверку.")
    return redirect("vpn_form_detail", pk=vpn_form.pk)


@approved_required
def vpn_review_list(request):
    if request.user.role not in [UserRole.COORDINATOR, UserRole.ADMIN] and not request.user.is_superuser:
        raise PermissionDenied
    forms = available_review_forms(_forms_for_user(request.user)).order_by("-date", "-submitted_at")
    return render(request, "questionnaires/vpn_review_list.html", {"forms": forms})


@approved_required
def vpn_form_review(request, pk):
    vpn_form = get_object_or_404(VpnTestForm, pk=pk)
    if not _can_review(request.user, vpn_form):
        raise PermissionDenied
    return vpn_form_detail(request, pk)


@approved_required
def vpn_measurement_confirm(request, pk):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    if not _can_review(request.user, measurement.form):
        raise PermissionDenied
    if measurement.status != MeasurementStatus.SUBMITTED:
        messages.info(request, "Согласовать можно только отправленный замер.")
        return redirect("vpn_measurement_summary", pk=measurement.pk)
    measurement.status = MeasurementStatus.CONFIRMED
    measurement.checked_by = request.user
    measurement.confirmed_at = timezone.now()
    measurement.save(update_fields=["status", "checked_by", "confirmed_at", "updated_at"])
    _sync_form_status_from_measurements(measurement.form, request.user)
    messages.success(request, "Замер согласован.")
    return redirect("vpn_form_detail", pk=measurement.form_id)


@approved_required
def vpn_measurement_return(request, pk):
    measurement = get_object_or_404(VpnMeasurement.objects.select_related("form"), pk=pk)
    if not _can_review(request.user, measurement.form):
        raise PermissionDenied
    if measurement.status != MeasurementStatus.SUBMITTED:
        messages.info(request, "Вернуть можно только отправленный замер.")
        return redirect("vpn_measurement_summary", pk=measurement.pk)
    if request.method == "POST":
        form = ReturnMeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.status = MeasurementStatus.RETURNED
            measurement.returned_at = timezone.now()
            measurement.checked_by = request.user
            measurement.save(update_fields=["status", "return_comment", "returned_at", "checked_by", "updated_at"])
            _sync_form_status_from_measurements(measurement.form, request.user)
            messages.warning(request, "Замер возвращен на доработку.")
            return redirect("vpn_form_detail", pk=measurement.form_id)
    else:
        form = ReturnMeasurementForm(instance=measurement)
    return render(request, "questionnaires/vpn_return.html", {"form": form, "title": "Возврат замера"})


@approved_required
def vpn_form_confirm(request, pk):
    vpn_form = get_object_or_404(VpnTestForm, pk=pk)
    if not _can_review(request.user, vpn_form):
        raise PermissionDenied
    if vpn_form.status == VpnFormStatus.CONFIRMED:
        messages.info(request, "Анкета уже подтверждена.")
        return redirect("vpn_form_detail", pk=vpn_form.pk)
    if vpn_form.status != VpnFormStatus.SUBMITTED:
        messages.info(request, "Подтвердить можно только отправленную анкету.")
        return redirect("vpn_form_detail", pk=vpn_form.pk)
    vpn_form.status = VpnFormStatus.CONFIRMED
    vpn_form.confirmed_by = request.user
    vpn_form.confirmed_at = timezone.now()
    vpn_form.save(update_fields=["status", "confirmed_by", "confirmed_at", "updated_at"])
    messages.success(request, "Анкета подтверждена.")
    return redirect("vpn_form_detail", pk=vpn_form.pk)


@approved_required
def vpn_form_return(request, pk):
    vpn_form = get_object_or_404(VpnTestForm, pk=pk)
    if not _can_review(request.user, vpn_form):
        raise PermissionDenied
    if vpn_form.status != VpnFormStatus.SUBMITTED:
        messages.info(request, "Вернуть можно только отправленную анкету.")
        return redirect("vpn_form_detail", pk=vpn_form.pk)
    if request.method == "POST":
        form = ReturnFormForm(request.POST)
        if form.is_valid():
            vpn_form.status = VpnFormStatus.RETURNED
            vpn_form.save(update_fields=["status", "updated_at"])
            vpn_form.measurements.filter(status=MeasurementStatus.SUBMITTED).update(
                status=MeasurementStatus.RETURNED,
                returned_at=timezone.now(),
                checked_by=request.user,
                return_comment=form.cleaned_data["comment"],
            )
            messages.warning(request, "Анкета возвращена на доработку.")
            return redirect("vpn_form_detail", pk=vpn_form.pk)
    else:
        form = ReturnFormForm()
    return render(request, "questionnaires/vpn_return.html", {"form": form, "title": "Возврат анкеты"})
