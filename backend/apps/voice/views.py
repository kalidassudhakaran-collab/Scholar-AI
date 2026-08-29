from apps.ai_tasks.base import BaseAIRunView
from apps.ai_tasks.tasks.voice import run_voice


class VoiceRunView(BaseAIRunView):
    feature = "voice"
    task_fn = run_voice
