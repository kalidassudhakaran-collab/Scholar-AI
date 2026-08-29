from rest_framework import serializers

from .models import AIHistory


class AIHistorySerializer(serializers.ModelSerializer):
    input_file_name = serializers.CharField(
        source="input_file.original_name", read_only=True, default=None
    )

    class Meta:
        model = AIHistory
        fields = (
            "id",
            "feature",
            "status",
            "input_text",
            "input_file",
            "input_file_name",
            "input_url",
            "input_metadata",
            "output_text",
            "output_metadata",
            "output_file_url",
            "task_id",
            "processing_time",
            "model_used",
            "is_starred",
            "user_note",
            "tags",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "output_text",
            "output_metadata",
            "output_file_url",
            "task_id",
            "processing_time",
            "model_used",
            "created_at",
            "updated_at",
        )


class AIHistoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIHistory
        fields = ("is_starred", "user_note", "tags")
