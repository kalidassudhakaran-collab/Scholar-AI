from celery import shared_task

from ai_engine.ocr_processor import process_file
from apps.ai_tasks.tasks._helpers import TaskProgress, get_input_file_path


@shared_task(bind=True, max_retries=2)
def run_ocr(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(15, "Reading file...")

        file_path = get_input_file_path(progress.history)
        if not file_path:
            raise ValueError("No file attached to this task.")

        progress.send(40, "Running OCR...")
        result = process_file(file_path)

        progress.send(90, "Saving result...")
        progress.history.output_text = result.get("full_text", "")
        progress.history.model_used = result.get("method", "ocr")
        progress.history.output_metadata = {
            "confidence": result.get("confidence"),
            "pages": len(result.get("pages", [])),
        }
        progress.history.save(
            update_fields=["output_text", "model_used", "output_metadata"]
        )
        progress.complete(
            {"output_text": progress.history.output_text, "metadata": progress.history.output_metadata}
        )
    except Exception as exc:
        progress.history.status = "failed"
        progress.history.output_text = f"Error: {exc}"
        progress.history.save(update_fields=["status", "output_text"])
        progress.fail()
        return
