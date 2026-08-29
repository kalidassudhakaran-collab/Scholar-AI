from celery import shared_task

from ai_engine.ai_detector import detect_ai_text
from apps.ai_tasks.tasks._helpers import TaskProgress, get_input_text


@shared_task(bind=True, max_retries=3)
def run_ai_detection(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(10, "Analyzing writing patterns...")

        text = get_input_text(progress.history)
        options = progress.history.input_metadata or {}
        sensitivity = options.get("sensitivity", "balanced")

        progress.send(45, "Running AI detector...")
        result = detect_ai_text(text, sensitivity=sensitivity)

        progress.send(90, "Saving result...")
        progress.history.output_text = result["output_text"]
        progress.history.model_used = result.get("model_used", "")
        progress.history.output_metadata = {
            "ai_probability": result.get("ai_probability", 0),
            "percentage": result.get("percentage", 0),
            "verdict": result.get("verdict", ""),
            "confidence": result.get("confidence", ""),
            "sensitivity": sensitivity,
            "segment_scores": result.get("segment_scores", [])[:20],
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
