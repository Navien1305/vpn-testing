from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "full_name", "organization", "role", "is_approved", "is_staff")
    list_filter = ("role", "is_approved", "is_staff", "organization", "mobile_operators")
    search_fields = ("username", "full_name", "contact")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Профиль тестирования",
            {"fields": ("full_name", "organization", "cities", "mobile_operators", "contact", "role", "is_approved")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Профиль тестирования",
            {"fields": ("full_name", "organization", "cities", "mobile_operators", "contact", "role", "is_approved")},
        ),
    )
