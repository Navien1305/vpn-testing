from django.contrib import admin

from .models import DailyFormPlan


@admin.register(DailyFormPlan)
class DailyFormPlanAdmin(admin.ModelAdmin):
    list_display = ("date", "form_type", "organization", "city", "mobile_operator", "os", "expected")
    list_filter = ("date", "form_type", "organization", "city", "mobile_operator", "os", "expected")
    search_fields = ("organization__name", "city__name", "mobile_operator__name")
    date_hierarchy = "date"
