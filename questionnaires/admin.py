from django.contrib import admin

from .models import TesterDevice, VpnMeasurement, VpnMeasurementResult, VpnTestForm


@admin.register(TesterDevice)
class TesterDeviceAdmin(admin.ModelAdmin):
    list_display = ("tester", "name", "created_at")
    search_fields = ("tester__username", "tester__full_name", "name")


class VpnMeasurementInline(admin.TabularInline):
    model = VpnMeasurement
    extra = 0


@admin.register(VpnTestForm)
class VpnTestFormAdmin(admin.ModelAdmin):
    list_display = ("date", "organization", "tester", "city", "mobile_operator", "os", "status")
    list_filter = ("status", "os", "organization", "city", "mobile_operator")
    search_fields = ("tester", "contact", "device")
    inlines = [VpnMeasurementInline]


@admin.register(VpnMeasurement)
class VpnMeasurementAdmin(admin.ModelAdmin):
    list_display = ("form", "measurement_number", "status", "submitted_at", "confirmed_at", "checked_by")
    list_filter = ("measurement_number", "status")
    search_fields = ("form__tester", "form__organization__name")


@admin.register(VpnMeasurementResult)
class VpnMeasurementResultAdmin(admin.ModelAdmin):
    list_display = ("measurement", "vpn_app", "vpn_unable_to_check", "web_without_vpn_status", "web_with_vpn_status", "instagram_status", "youtube_status", "measured_at")
    list_filter = ("vpn_unable_to_check", "web_without_vpn_status", "web_with_vpn_status", "instagram_status", "youtube_status")
    search_fields = ("vpn_app__name", "vpn_app__package_id", "comment")
