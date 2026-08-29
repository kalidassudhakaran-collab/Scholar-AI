from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_engine.paraphraser import STYLE_PROMPTS
from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.paraphrase import run_paraphrase


class ParaphraseView(BaseAIRunView):
    feature = "paraphraser"
    task_fn = run_paraphrase


class ParaphraserStylesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "styles": [
                    {"id": key, "label": key.capitalize()}
                    for key in STYLE_PROMPTS
                ]
            }
        )
