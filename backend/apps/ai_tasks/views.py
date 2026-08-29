from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.history.models import AIHistory
from apps.history.serializers import AIHistorySerializer


class TaskStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            history = AIHistory.objects.get(task_id=task_id, user=request.user)
        except AIHistory.DoesNotExist:
            return Response({"detail": "Task not found."}, status=404)

        progress = 100 if history.status == "completed" else 0
        if history.status == "processing":
            progress = 50

        # Local async threads use a UUID task_id — not a Celery result; trust DB status only.
        if not getattr(settings, "CELERY_TASK_EAGER_ASYNC", False):
            from celery.result import AsyncResult

            result = AsyncResult(task_id)
            if result.failed() and history.status not in ("failed", "completed"):
                history.status = "failed"
                history.save(update_fields=["status"])

        payload = {
            "task_id": task_id,
            "status": history.status,
            "progress": progress,
        }
        if history.status == "completed":
            payload["result"] = {
                "output_text": history.output_text,
                "metadata": history.output_metadata,
            }
            payload["model_used"] = history.model_used or ""
        elif history.status == "failed":
            err = (history.output_text or "").strip()
            if err.lower().startswith("error:"):
                err = err[6:].strip()
            payload["error"] = err or "Task failed"

        return Response(payload)
