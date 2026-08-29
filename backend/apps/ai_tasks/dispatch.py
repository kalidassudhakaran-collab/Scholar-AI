import threading
import uuid

from django.conf import settings

from apps.history.models import AIHistory


def start_ai_task(task_fn, history_id: str) -> str:
    """Queue an AI task; returns task_id for polling."""
    hid = str(history_id)

    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False) and getattr(
        settings, "CELERY_TASK_EAGER_ASYNC", False
    ):
        task_id = str(uuid.uuid4())
        AIHistory.objects.filter(id=hid).update(task_id=task_id)

        def _run():
            try:
                task_fn.apply(args=(hid,))
            except Exception as exc:
                AIHistory.objects.filter(id=hid).update(
                    status="failed",
                    output_text=f"Error: {exc}",
                )

        threading.Thread(target=_run, daemon=True).start()
        return task_id

    task = task_fn.delay(hid)
    AIHistory.objects.filter(id=hid).update(task_id=task.id)
    return task.id
