from celery import shared_task

from ai_engine.summarizer import summarize
from apps.ai_tasks.tasks._helpers import TaskProgress, get_input_text


@shared_task(bind=True, max_retries=3)
def run_summarize(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(10, "Loading summarizer model...")

        text = get_input_text(progress.history)
        options = progress.history.input_metadata or {}
        summary_type = options.get("summary_type", "detailed")
        max_length = options.get("max_length")

        progress.send(40, "Summarizing document...")
        result = summarize(text, summary_type=summary_type, max_length=max_length)

        progress.send(90, "Saving result...")
        progress.history.output_text = result["output_text"]
        progress.history.model_used = result.get("model_used", "")
        progress.history.output_metadata = {
            "summary_type": summary_type,
            "word_count": len(text.split()),
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
        progress.history.status = "failed"
        progress.history.output_text = f"Error: {exc}"
        progress.history.save(update_fields=["status", "output_text"])
        progress.fail()
        return
