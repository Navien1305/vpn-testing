from django.utils import timezone

from references.models import VpnAppPeriod

from .models import CheckStatus, VpnFormStatus, VpnMeasurementResult


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


def update_form_status_after_measurement_submit(vpn_form):
    vpn_form.status = VpnFormStatus.SUBMITTED
    vpn_form.submitted_at = timezone.now()
    vpn_form.save(update_fields=["status", "submitted_at", "updated_at"])


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
