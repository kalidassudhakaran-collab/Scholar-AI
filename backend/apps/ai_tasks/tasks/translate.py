from celery import shared_task

from ai_engine.translator import translate
from apps.ai_tasks.tasks._helpers import TaskProgress, get_input_text


@shared_task(bind=True, max_retries=3)
def run_translate(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(10, "Loading translation model...")

        text = get_input_text(progress.history)
        options = progress.history.input_metadata or {}
        source_lang = options.get("source_language", "en")
        target_lang = options.get("target_language", "es")

        progress.send(40, f"Translating {source_lang} → {target_lang}...")
        result = translate(text, source_lang, target_lang)

        progress.send(90, "Saving result...")
        progress.history.output_text = result["output_text"]
        progress.history.model_used = result.get("model_used", "")
        progress.history.output_metadata = {
            "source_language": result.get("source_language"),
            "target_language": result.get("target_language"),
            "word_count": result.get("word_count", 0),
        }
        progress.history.save(
            update_fields=["output_text", "model_used", "output_metadata"]
        )
        progress.complete(
            {
                "output_text": result["output_text"],
                "metadata": progress.history.output_metadata,
                "model_used": result.get("model_used", ""),
            }
        )
    except Exception as exc:
        progress.fail()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
