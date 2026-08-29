from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.ai_detection import run_ai_detection


class AiDetectionRunView(BaseAIRunView):
    feature = "ai_detection"
    task_fn = run_ai_detection
