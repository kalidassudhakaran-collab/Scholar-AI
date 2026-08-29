import csv
import io

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ai_tasks.dispatch import start_ai_task
from apps.ai_tasks.tasks.ai_detection import run_ai_detection
from apps.ai_tasks.tasks.humanize import run_humanize
from apps.ai_tasks.tasks.paraphrase import run_paraphrase
from apps.ai_tasks.tasks.plagiarism import run_plagiarism
from apps.ai_tasks.tasks.summarize import run_summarize
from apps.ai_tasks.tasks.translate import run_translate
from apps.ai_tasks.tasks.youtube import run_youtube

from .filters import AIHistoryFilter
from .models import AIHistory
from .serializers import AIHistorySerializer, AIHistoryUpdateSerializer

FEATURE_TASKS = {
    "summarizer": run_summarize,
    "translator": run_translate,
    "paraphraser": run_paraphrase,
    "humanizer": run_humanize,
    "plagiarism": run_plagiarism,
    "ai_detection": run_ai_detection,
    "youtube": run_youtube,
}


class AIHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AIHistorySerializer
    filterset_class = AIHistoryFilter
    search_fields = ["input_text", "output_text", "user_note"]
    ordering_fields = ["created_at", "feature", "status"]

    def get_queryset(self):
        return AIHistory.objects.filter(user=self.request.user).select_related("input_file")

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return AIHistoryUpdateSerializer
        return AIHistorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def rerun(self, request, pk=None):
        history = self.get_object()
        task_fn = FEATURE_TASKS.get(history.feature)
        if not task_fn:
            return Response(
                {"detail": f"Re-run is not supported for {history.feature}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_entry = AIHistory.objects.create(
            user=request.user,
            feature=history.feature,
            status="pending",
            input_text=history.input_text,
            input_file=history.input_file,
            input_url=history.input_url,
            input_metadata=history.input_metadata,
        )
        task_id = start_ai_task(task_fn, new_entry.id)
        new_entry.refresh_from_db()

        return Response(
            {
                **AIHistorySerializer(new_entry).data,
                "task_id": task_id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def export(self, request):
        qs = self.filter_queryset(self.get_queryset())[:500]
        fmt = request.query_params.get("format", "txt").lower()

        if fmt == "csv":
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(
                [
                    "id",
                    "feature",
                    "status",
                    "created_at",
                    "input_text",
                    "output_text",
                    "model_used",
                    "is_starred",
                ]
            )
            for h in qs:
                writer.writerow(
                    [
                        str(h.id),
                        h.feature,
                        h.status,
                        h.created_at.isoformat(),
                        (h.input_text or "")[:5000],
                        (h.output_text or "")[:5000],
                        h.model_used or "",
                        h.is_starred,
                    ]
                )
            response = HttpResponse(buffer.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="scholar-ai-history.csv"'
            return response

        lines = []
        for h in qs:
            lines.append(
                f"=== {h.feature.upper()} | {h.created_at:%Y-%m-%d %H:%M} | {h.status} ===\n"
                f"INPUT:\n{h.input_text or '(file/url)'}\n\n"
                f"OUTPUT:\n{h.output_text or '(pending)'}\n"
            )
        response = HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="scholar-ai-history.txt"'
        return response

    @action(detail=False, methods=["delete"])
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "No ids provided."}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = AIHistory.objects.filter(user=request.user, id__in=ids).delete()
        return Response({"deleted": deleted})
