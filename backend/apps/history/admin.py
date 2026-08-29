from django.contrib import admin

from .models import AIHistory


@admin.register(AIHistory)
class AIHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "feature", "status", "created_at")
    list_filter = ("feature", "status", "is_starred")
    search_fields = ("user__email", "input_text", "output_text")
    readonly_fields = ("created_at", "updated_at")
