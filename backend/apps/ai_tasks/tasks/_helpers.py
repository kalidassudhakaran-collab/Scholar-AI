import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.history.models import AIHistory


def get_input_file_path(history: AIHistory) -> str | None:
    if history.input_file and history.input_file.file:
        return history.input_file.file.path
    return None


def extract_text_from_uploaded_file(uploaded_file) -> str:
    """
    Best-effort text extraction for document uploads used by text tools.
    Caches extracted text on the UploadedFile record to speed up re-runs/history.
    """
    try:
        cached = (uploaded_file.extracted_text or "").strip()
        if cached:
            return cached
    except Exception:
        pass

    f = getattr(uploaded_file, "file", None)
    if not f:
        return ""

    name = (getattr(uploaded_file, "original_name", "") or getattr(f, "name", "") or "").lower()
    mime = (getattr(uploaded_file, "mime_type", "") or "").lower()

    text = ""
    try:
        # Plain text / markdown
        if name.endswith((".txt", ".md")) or mime in ("text/plain", "text/markdown"):
            f.open("r")
            try:
                text = f.read()
            finally:
                f.close()

        # PDF
        elif name.endswith(".pdf") or mime == "application/pdf":
            import pdfplumber

            path = f.path
            chunks = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        chunks.append(page_text)
            text = "\n\n".join(chunks)

        # DOCX (Word)
        elif name.endswith(".docx") or mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            from docx import Document  # python-docx

            path = f.path
            doc = Document(path)
            chunks = []
            for p in doc.paragraphs:
                if p.text and p.text.strip():
                    chunks.append(p.text)
            text = "\n".join(chunks)
    except Exception:
        text = ""

    text = (text or "").strip()
    if text:
        try:
            uploaded_file.extracted_text = text
            uploaded_file.save(update_fields=["extracted_text"])
        except Exception:
            pass

    return text


def get_input_text(history: AIHistory) -> str:
    if history.input_text and history.input_text.strip():
        return history.input_text.strip()
    if history.input_file:
        return extract_text_from_uploaded_file(history.input_file)
    return ""


class TaskProgress:
    def __init__(self, task, history_id: str):
        self.task = task
        self.history = AIHistory.objects.get(id=history_id)
        self.user_id = str(self.history.user_id)
        self.channel_layer = get_channel_layer()
        self.start = time.time()

    def send(self, progress: int, message: str):
        if not self.channel_layer:
            return
        async_to_sync(self.channel_layer.group_send)(
            f"user_{self.user_id}",
            {
                "type": "task_update",
                "event": "task.update",
                "task_id": self.task.request.id,
                "progress": progress,
                "message": message,
                "status": "processing",
            },
        )

    def complete(self, result: dict):
        self.history.status = "completed"
        self.history.processing_time = time.time() - self.start
        self.history.save(update_fields=["status", "processing_time"])

        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f"user_{self.user_id}",
                {
                    "type": "task_complete",
                    "event": "task.complete",
                    "task_id": self.task.request.id,
                    "history_id": str(self.history.id),
                    "progress": 100,
                    "result": result,
                    "model_used": result.get("model_used", ""),
                },
            )

    def fail(self):
        self.history.status = "failed"
        self.history.save(update_fields=["status"])
