from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.youtube import run_youtube


class YoutubeRunView(BaseAIRunView):
    feature = "youtube"
    task_fn = run_youtube
