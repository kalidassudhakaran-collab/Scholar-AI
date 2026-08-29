from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.humanize import run_humanize


class HumanizeView(BaseAIRunView):
    feature = "humanizer"
    task_fn = run_humanize
