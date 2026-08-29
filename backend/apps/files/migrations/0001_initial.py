import uuid

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
            name="UploadedFile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("original_name", models.CharField(max_length=500)),
                ("stored_name", models.CharField(max_length=500)),
                ("file", models.FileField(upload_to="uploads/%Y/%m/")),
                ("storage_url", models.URLField(blank=True, max_length=1000, null=True)),
                (
                    "file_type",
                    models.CharField(
                        choices=[
                            ("pdf", "PDF"),
                            ("image", "Image"),
                            ("audio", "Audio"),
                            ("video", "Video"),
                            ("document", "Document"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=50,
                    ),
                ),
                ("mime_type", models.CharField(blank=True, max_length=100)),
                ("size_bytes", models.BigIntegerField(default=0)),
                ("extracted_text", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="uploaded_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "files_uploadedfile",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "-created_at"], name="files_uploa_user_id_8a1f0d_idx")
                ],
            },
        ),
    ]
