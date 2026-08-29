import uuid

from django.conf import settings
from django.db import models


class UploadedFile(models.Model):
    FILE_TYPES = [
        ("pdf", "PDF"),
        ("image", "Image"),
        ("audio", "Audio"),
        ("video", "Video"),
        ("document", "Document"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
    )
    original_name = models.CharField(max_length=500)
    stored_name = models.CharField(max_length=500)
    file = models.FileField(upload_to="uploads/%Y/%m/")
    storage_url = models.URLField(max_length=1000, blank=True, null=True)
    file_type = models.CharField(max_length=50, choices=FILE_TYPES, default="other")
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.BigIntegerField(default=0)
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "files_uploadedfile"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return self.original_name
