import uuid

from django.conf import settings
from django.db import models


class AIHistory(models.Model):
    FEATURE_CHOICES = [
        ("summarizer", "Summarizer"),
        ("translator", "Translator"),
        ("paraphraser", "Paraphraser"),
        ("humanizer", "Humanizer"),
        ("plagiarism", "Plagiarism"),
        ("ai_detection", "AI Detection"),
        ("ocr", "OCR"),
        ("voice", "Voice"),
        ("youtube", "YouTube"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_history",
    )
    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    input_text = models.TextField(blank=True, null=True)
    input_file = models.ForeignKey(
        "files.UploadedFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_entries",
    )
    input_url = models.URLField(max_length=2000, blank=True, null=True)
    input_metadata = models.JSONField(default=dict, blank=True)

    output_text = models.TextField(blank=True, null=True)
    output_metadata = models.JSONField(default=dict, blank=True)
    output_file_url = models.URLField(max_length=1000, blank=True, null=True)

    task_id = models.CharField(max_length=255, blank=True, null=True)
    processing_time = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True, null=True)
    tokens_processed = models.IntegerField(null=True, blank=True)

    is_starred = models.BooleanField(default=False)
    user_note = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "history_aihistory"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "feature"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.feature} — {self.status} ({self.id})"
