from rest_framework import status
from rest_framework.response import Response

from apps.ai_tasks.base import AIRunRequestSerializer, BaseAIRunView
from apps.ai_tasks.tasks.plagiarism import run_plagiarism


class PlagiarismRunView(BaseAIRunView):
    feature = "plagiarism"
    task_fn = run_plagiarism

    def post(self, request):
        serializer = AIRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comparison = (serializer.validated_data.get("options") or {}).get(
            "comparison_text", ""
        )
        comparison_file_id = (serializer.validated_data.get("options") or {}).get(
            "comparison_file_id"
        )
        if not str(comparison).strip() and not comparison_file_id:
            return Response(
                {"detail": "Provide Document B as options.comparison_text or options.comparison_file_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().post(request)
