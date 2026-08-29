from celery import shared_task

from ai_engine.plagiarism_detector import check_plagiarism
from apps.ai_tasks.tasks._helpers import TaskProgress, extract_text_from_uploaded_file, get_input_text


@shared_task(bind=True, max_retries=3)
def run_plagiarism(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(10, "Analyzing documents...")

        text_a = get_input_text(progress.history)
        options = progress.history.input_metadata or {}
        text_b = (options.get("comparison_text") or "").strip()
        comparison_file_id = options.get("comparison_file_id")
        threshold = options.get("threshold")
        threshold = float(threshold) if threshold is not None else None

        if not text_b and comparison_file_id:
            from apps.files.models import UploadedFile

            try:
                comparison_file = UploadedFile.objects.get(
                    id=comparison_file_id, user=progress.history.user
                )
            except UploadedFile.DoesNotExist:
                raise ValueError("comparison_file_id not found.")
            text_b = extract_text_from_uploaded_file(comparison_file).strip()

        if not text_b:
            raise ValueError("Document B is required (comparison_text or comparison_file_id).")

        progress.send(40, "Comparing sentences...")
        result = check_plagiarism(text_a, text_b, threshold=threshold)

        progress.send(90, "Saving result...")
        progress.history.output_text = result["output_text"]
        progress.history.model_used = result.get("model_used", "")
        progress.history.output_metadata = {
            "percentage": float(result.get("percentage", 0)),
            "matched_sentences": int(result.get("matched_sentences", 0)),
            "total_sentences": int(result.get("total_sentences", 0)),
            "matches": result.get("matches", [])[:50],
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
