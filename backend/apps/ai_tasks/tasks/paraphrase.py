from celery import shared_task

from ai_engine.paraphraser import paraphrase
from apps.ai_tasks.tasks._helpers import TaskProgress, get_input_text


@shared_task(bind=True, max_retries=3)
def run_paraphrase(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(10, "Loading paraphrase model...")

        text = get_input_text(progress.history)
        options = progress.history.input_metadata or {}
        style = options.get("style", "fluent")

        progress.send(40, f"Paraphrasing ({style})...")
        result = paraphrase(text, style=style)

        progress.send(90, "Saving result...")
        progress.history.output_text = result["output_text"]
        progress.history.model_used = result.get("model_used", "")
        progress.history.output_metadata = {"style": result.get("style", style)}
        progress.history.save(
            update_fields=["output_text", "model_used", "output_metadata"]
        )
        progress.complete(
            {"output_text": result["output_text"], "metadata": progress.history.output_metadata}
        )
    except Exception as exc:
        progress.fail()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
