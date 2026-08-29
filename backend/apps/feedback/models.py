from django.conf import settings
from django.db import models


class Feedback(models.Model):
    FEATURE_CHOICES = [
        ("general", "General"),
        ("summarizer", "Summarizer"),
        ("translator", "Translator"),
        ("paraphraser", "Paraphraser"),
        ("humanizer", "Humanizer"),
        ("ai_detection", "AI Detection"),
        ("plagiarism", "Plagiarism"),
        ("ocr", "OCR"),
        ("voice", "Voice"),
        ("youtube", "YouTube"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    feature = models.CharField(max_length=32, choices=FEATURE_CHOICES, default="general")
    likes = models.TextField(blank=True)
    drawbacks = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id} — {self.feature} ({self.created_at:%Y-%m-%d})"
