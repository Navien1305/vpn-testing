from django.utils import timezone

from references.models import Messenger, VpnAppPeriod

from .models import CheckStatus, MeasurementStatus, MessengerFormStatus, MessengerTestResult, VpnFormStatus, VpnMeasurementResult


def log_action(action, user, obj, details=""):
    # Hook for future audit log integration.
    return None


def get_period_vpn_apps(vpn_form):
    return (
        VpnAppPeriod.objects.select_related("vpn_app")
        .filter(
            active_from__lte=vpn_form.date,
            active_to__gte=vpn_form.date,
            is_active=True,
            vpn_app__os=vpn_form.os,
        )
        .order_by("display_order", "vpn_app__name")
    )


def ensure_measurement_results(measurement):
    period_apps = get_period_vpn_apps(measurement.form)
    for period_app in period_apps:
        VpnMeasurementResult.objects.get_or_create(measurement=measurement, vpn_app=period_app.vpn_app)
    return period_apps


def ordered_results(measurement):
    period_apps = list(get_period_vpn_apps(measurement.form))
    ensure_measurement_results(measurement)
    results_by_app_id = {
        result.vpn_app_id: result
        for result in VpnMeasurementResult.objects.select_related("vpn_app").filter(measurement=measurement)
    }
    return [results_by_app_id[period_app.vpn_app_id] for period_app in period_apps if period_app.vpn_app_id in results_by_app_id]


def mark_all_results_available(measurement):
    for result in ordered_results(measurement):
        result.vpn_unable_to_check = False
        result.web_without_vpn_status = CheckStatus.WORKS
        result.web_with_vpn_status = CheckStatus.WORKS
        result.instagram_status = CheckStatus.WORKS
        result.youtube_status = CheckStatus.WORKS
        result.save()


def measurement_progress(measurement):
    results = ordered_results(measurement)
    total = len(results)
    filled = sum(1 for result in results if result.is_filled)
    return {
        "total": total,
        "filled": filled,
        "empty": total - filled,
        "percent": round((filled / total) * 100) if total else 0,
    }


def can_submit_measurement(measurement):
    progress = measurement_progress(measurement)
    baseline_ok = bool(measurement.onelostbox_without_vpn_status) and (
        measurement.onelostbox_without_vpn_status != CheckStatus.UNABLE_TO_CHECK
        or bool(measurement.onelostbox_without_vpn_comment.strip())
    )
    return baseline_ok and progress["total"] > 0 and progress["empty"] == 0


def update_vpn_form_status_from_measurements(vpn_form, finish_with_first_only=False):
    measurements = list(vpn_form.measurements.all())
    submitted_numbers = {
        measurement.measurement_number
        for measurement in measurements
        if measurement.status in [MeasurementStatus.SUBMITTED, MeasurementStatus.CONFIRMED]
    }

    if finish_with_first_only and 1 in submitted_numbers:
        vpn_form.status = VpnFormStatus.SUBMITTED
        vpn_form.submitted_at = timezone.now()
        vpn_form.save(update_fields=["status", "submitted_at", "updated_at"])
        return

    if 2 in submitted_numbers:
        vpn_form.status = VpnFormStatus.SUBMITTED
        vpn_form.submitted_at = timezone.now()
        vpn_form.save(update_fields=["status", "submitted_at", "updated_at"])
        return

    if 1 in submitted_numbers:
        vpn_form.status = VpnFormStatus.PARTIALLY_SUBMITTED
        vpn_form.submitted_at = timezone.now()
        vpn_form.save(update_fields=["status", "submitted_at", "updated_at"])
        return

    if vpn_form.status not in [VpnFormStatus.DRAFT, VpnFormStatus.RETURNED]:
        vpn_form.status = VpnFormStatus.DRAFT
        vpn_form.save(update_fields=["status", "updated_at"])


def complete_measurement_if_ready(measurement):
    if not can_submit_measurement(measurement):
        return False
    if measurement.status not in [MeasurementStatus.SUBMITTED, MeasurementStatus.CONFIRMED]:
        measurement.status = MeasurementStatus.SUBMITTED
        measurement.submitted_at = timezone.now()
        measurement.confirmed_at = None
        measurement.returned_at = None
        measurement.return_comment = ""
        measurement.checked_by = None
        measurement.save(
            update_fields=[
                "status",
                "submitted_at",
                "confirmed_at",
                "returned_at",
                "return_comment",
                "checked_by",
                "updated_at",
            ]
        )
    update_vpn_form_status_from_measurements(measurement.form)
    return True


def update_form_status_after_measurement_submit(vpn_form):
    update_vpn_form_status_from_measurements(vpn_form)


def form_measurement_summary(vpn_form):
    summaries = {}
    for measurement in vpn_form.measurements.all():
        summaries[measurement.measurement_number] = {
            "measurement": measurement,
            "progress": measurement_progress(measurement),
        }
    return summaries


def available_review_forms(queryset):
    return queryset.filter(status=VpnFormStatus.SUBMITTED)


def ensure_messenger_results(form):
    for messenger in Messenger.objects.filter(is_active=True).order_by("display_order", "name"):
        MessengerTestResult.objects.get_or_create(form=form, messenger=messenger)


def ordered_messenger_results(form):
    ensure_messenger_results(form)
    active_messengers = list(Messenger.objects.filter(is_active=True).order_by("display_order", "name"))
    results_by_messenger_id = {
        result.messenger_id: result
        for result in MessengerTestResult.objects.select_related("messenger").filter(form=form)
    }
    return [results_by_messenger_id[messenger.id] for messenger in active_messengers if messenger.id in results_by_messenger_id]


def messenger_form_progress(form):
    results = ordered_messenger_results(form)
    total = len(results)
    filled = sum(1 for result in results if result.is_filled)
    return {
        "total": total,
        "filled": filled,
        "empty": total - filled,
        "percent": round((filled / total) * 100) if total else 0,
    }


def can_submit_messenger_form(form):
    progress = messenger_form_progress(form)
    return progress["total"] > 0 and progress["empty"] == 0


def available_messenger_review_forms(queryset):
    return queryset.filter(status=MessengerFormStatus.SUBMITTED)
