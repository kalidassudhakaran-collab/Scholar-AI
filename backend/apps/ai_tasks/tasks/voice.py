from celery import shared_task

from ai_engine.speech_processor import transcribe
from apps.ai_tasks.tasks._helpers import TaskProgress, get_input_file_path


@shared_task(bind=True, max_retries=2)
def run_voice(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        progress.send(10, "Loading Whisper model...")

        file_path = get_input_file_path(progress.history)
        if not file_path:
            raise ValueError("No audio file attached.")

        options = progress.history.input_metadata or {}
        language = options.get("language")
        model_size = options.get("model_size", "small")

        progress.send(35, "Transcribing audio...")
        result = transcribe(file_path, language=language, model_size=model_size)

        progress.send(90, "Saving transcript...")
        progress.history.output_text = result.get("text", "")
        progress.history.model_used = result.get("method", "whisper")
        progress.history.output_metadata = {
            "language": result.get("language"),
            "duration": result.get("duration"),
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
