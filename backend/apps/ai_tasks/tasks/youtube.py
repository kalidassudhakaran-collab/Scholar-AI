from celery import shared_task

from ai_engine.summarizer import summarize
from ai_engine.youtube_processor import process
from apps.ai_tasks.tasks._helpers import TaskProgress


@shared_task(bind=True, max_retries=2)
def run_youtube(self, history_id: str):
    progress = TaskProgress(self, history_id)
    try:
        progress.history.status = "processing"
        progress.history.save(update_fields=["status"])
        url = progress.history.input_url or ""
        if not url:
            raise ValueError("YouTube URL is required.")

        progress.send(20, "Fetching transcript...")

        def summarize_fn(text):
            return summarize(text, summary_type="detailed")["output_text"]

        progress.send(50, "Processing video...")
        result = process(url, summarize_fn=summarize_fn)

        if result.get("error"):
            raise ValueError(result["error"])

        transcript = result.get("transcript", "") or ""
        output_parts = [
            f"# Summary\n{result.get('summary', '')}",
            "\n## Key points\n" + "\n".join(f"- {p}" for p in result.get("key_points", [])),
            f"\n## Full transcript\n{transcript}",
        ]
        output_text = "\n".join(output_parts)

        progress.send(90, "Saving result...")
        progress.history.output_text = output_text
        progress.history.model_used = "youtube-pipeline"
        progress.history.output_metadata = {
            "video_id": result.get("video_id"),
            "key_points": result.get("key_points", []),
            "transcript_word_count": len(transcript.split()),
        }
        progress.history.save(
            update_fields=["output_text", "model_used", "output_metadata"]
        )
        progress.complete(
            {"output_text": output_text, "metadata": progress.history.output_metadata}
        )
    except Exception as exc:
        progress.history.status = "failed"
        progress.history.output_text = f"Error: {exc}"
        progress.history.save(update_fields=["status", "output_text"])
        progress.fail()
        return
