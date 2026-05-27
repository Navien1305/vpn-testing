from django.contrib import admin

from .models import ExportLog


@admin.register(ExportLog)
class ExportLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "created_by",
        "export_type",
        "date_from",
        "date_to",
        "file_name",
        "rows_vpn",
        "rows_messenger",
        "status",
    )
    list_filter = ("export_type", "status", "date_from", "date_to")
    search_fields = ("file_name", "created_by__username", "created_by__full_name", "error_message")
    readonly_fields = (
        "created_at",
        "created_by",
        "export_type",
        "date_from",
        "date_to",
        "filters_json",
        "file_name",
        "rows_vpn",
        "rows_messenger",
        "status",
        "error_message",
    )
