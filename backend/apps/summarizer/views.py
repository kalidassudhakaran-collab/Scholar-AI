from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.summarize import run_summarize


class SummarizeView(BaseAIRunView):
    feature = "summarizer"
    task_fn = run_summarize


class SummarizerOptionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "summary_types": [
                    {"id": "short", "label": "Short"},
                    {"id": "detailed", "label": "Detailed"},
                    {"id": "bullets", "label": "Bullet points"},
                ]
            }
        )
