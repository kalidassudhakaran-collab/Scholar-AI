from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.translator import LANGUAGE_LABELS, SUPPORTED_PAIRS
from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.translate import run_translate


class TranslateView(BaseAIRunView):
    feature = "translator"
    task_fn = run_translate


class TranslatorLanguagesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        pairs = [
            {"source": src, "target": tgt, "model": model}
            for (src, tgt), model in sorted(SUPPORTED_PAIRS.items())
        ]
        return Response(
            {
                "languages": [
                    {"code": code, "label": label}
                    for code, label in sorted(LANGUAGE_LABELS.items())
                ],
                "pairs": pairs,
            }
        )
