import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feature",
                    models.CharField(
                        choices=[
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
                        ],
                        default="general",
                        max_length=32,
                    ),
                ),
                ("likes", models.TextField(blank=True)),
                ("drawbacks", models.TextField(blank=True)),
                ("improvements", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
