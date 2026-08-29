from django.core.exceptions import ValidationError

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
    "audio/mpeg",
    "audio/wav",
    "audio/mp4",
    "audio/ogg",
    "audio/x-wav",
}


def validate_upload_size(file, max_size: int):
    if file.size > max_size:
        raise ValidationError(f"File too large. Maximum size is {max_size // (1024 * 1024)} MB.")


def validate_mime_type(file):
    try:
        import magic

        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
    except ImportError:
        mime = getattr(file, "content_type", "") or "application/octet-stream"

    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(f"File type not allowed: {mime}")
