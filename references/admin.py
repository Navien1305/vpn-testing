from django.contrib import admin

from .models import City, Messenger, MobileOperator, Organization, VpnApp, VpnAppPeriod


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "city", "linked_mobile_operator", "is_active")
    list_filter = ("type", "is_active", "city", "linked_mobile_operator")
    search_fields = ("name",)


@admin.register(MobileOperator)
class MobileOperatorAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    filter_horizontal = ("cities",)


@admin.register(VpnApp)
class VpnAppAdmin(admin.ModelAdmin):
    list_display = ("name", "os", "package_id", "store_url")
    list_filter = ("os",)
    search_fields = ("name", "package_id")
    ordering = ("os", "name")


@admin.register(VpnAppPeriod)
class VpnAppPeriodAdmin(admin.ModelAdmin):
    list_display = ("vpn_app", "active_from", "active_to", "source_tag", "is_active", "display_order")
    list_filter = ("vpn_app__os", "source_tag", "is_active", "active_from", "active_to")
    search_fields = ("vpn_app__name", "vpn_app__package_id")
    ordering = ("-active_from", "vpn_app__os", "display_order")


@admin.register(Messenger)
class MessengerAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("display_order", "name")
