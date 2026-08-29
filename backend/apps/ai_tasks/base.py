from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_tasks.dispatch import start_ai_task
from apps.history.models import AIHistory


class AIRunRequestSerializer(serializers.Serializer):
    input_type = serializers.ChoiceField(choices=["text", "file", "url"], default="text")
    text = serializers.CharField(required=False, allow_blank=True)
    file_id = serializers.UUIDField(required=False, allow_null=True)
    url = serializers.URLField(required=False, allow_blank=True)
    options = serializers.JSONField(required=False, default=dict)

    def validate(self, attrs):
        input_type = attrs.get("input_type", "text")
        if input_type == "text" and not attrs.get("text"):
            raise serializers.ValidationError({"text": "Text is required for text input."})
        if input_type == "file" and not attrs.get("file_id"):
            raise serializers.ValidationError({"file_id": "file_id is required for file input."})
        if input_type == "url" and attrs.get("url") == "":
            attrs["url"] = None
        if input_type == "url" and not attrs.get("url"):
            raise serializers.ValidationError({"url": "url is required for url input."})
        return attrs


class BaseAIRunView(APIView):
    permission_classes = [IsAuthenticated]
    feature: str = ""
    task_fn = None

    def post(self, request):
        serializer = AIRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        input_file = None
        if data.get("file_id"):
            from apps.files.models import UploadedFile

            try:
                input_file = UploadedFile.objects.get(id=data["file_id"], user=request.user)
            except UploadedFile.DoesNotExist:
                return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        history = AIHistory.objects.create(
            user=request.user,
            feature=self.feature,
            status="pending",
            input_text=data.get("text") or "",
            input_file=input_file,
            input_url=data.get("url") or None,
            input_metadata=data.get("options") or {},
        )

        if self.task_fn:
            task_id = start_ai_task(self.task_fn, history.id)
        else:
            task_id = None

        return Response(
            {
                "task_id": task_id,
                "history_id": str(history.id),
                "status": "pending",
                "estimated_seconds": 8,
            },
            status=status.HTTP_202_ACCEPTED,
        )
