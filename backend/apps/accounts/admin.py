from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "plan", "is_verified", "is_staff")
    list_filter = ("plan", "is_verified", "is_staff")
    search_fields = ("email", "username", "full_name")
    ordering = ("email",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Scholar AI", {"fields": ("full_name", "avatar", "plan", "is_verified", "daily_requests")}),
    )
