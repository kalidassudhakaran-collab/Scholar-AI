from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "feature", "created_at")
    list_filter = ("feature", "created_at")
    search_fields = ("user__email", "likes", "drawbacks", "improvements")
    readonly_fields = ("user", "feature", "likes", "drawbacks", "improvements", "created_at")
