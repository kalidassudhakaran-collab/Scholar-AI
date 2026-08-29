from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.ocr import run_ocr


class OcrRunView(BaseAIRunView):
    feature = "ocr"
    task_fn = run_ocr
