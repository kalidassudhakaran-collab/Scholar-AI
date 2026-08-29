import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("files", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AIHistory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "feature",
                    models.CharField(
                        choices=[
                            ("summarizer", "Summarizer"),
                            ("translator", "Translator"),
                            ("paraphraser", "Paraphraser"),
                            ("humanizer", "Humanizer"),
                            ("plagiarism", "Plagiarism"),
                            ("ocr", "OCR"),
                            ("voice", "Voice"),
                            ("youtube", "YouTube"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("input_text", models.TextField(blank=True, null=True)),
                ("input_url", models.URLField(blank=True, max_length=2000, null=True)),
                ("input_metadata", models.JSONField(blank=True, default=dict)),
                ("output_text", models.TextField(blank=True, null=True)),
                ("output_metadata", models.JSONField(blank=True, default=dict)),
                ("output_file_url", models.URLField(blank=True, max_length=1000, null=True)),
                ("task_id", models.CharField(blank=True, max_length=255, null=True)),
                ("processing_time", models.FloatField(blank=True, null=True)),
                ("model_used", models.CharField(blank=True, max_length=100, null=True)),
                ("tokens_processed", models.IntegerField(blank=True, null=True)),
                ("is_starred", models.BooleanField(default=False)),
                ("user_note", models.TextField(blank=True, null=True)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "input_file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="history_entries",
                        to="files.uploadedfile",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "history_aihistory",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "feature"], name="history_aih_user_id_0e8b2a_idx"),
                    models.Index(
                        fields=["user", "-created_at"], name="history_aih_user_id_1c4f3d_idx"
                    ),
                ],
            },
        ),
    ]
