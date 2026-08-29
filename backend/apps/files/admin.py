from django.contrib import admin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "user", "file_type", "size_bytes", "created_at")
    list_filter = ("file_type",)
    search_fields = ("original_name", "user__email")
