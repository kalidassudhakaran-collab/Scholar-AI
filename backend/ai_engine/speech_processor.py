import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import whisper

    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

_whisper_model = None
_whisper_model_size: str | None = None


def _get_model(model_size: str = "small"):
    global _whisper_model, _whisper_model_size
    if not HAS_WHISPER:
        return None
    if _whisper_model is None or _whisper_model_size != model_size:
        from django.conf import settings

        root = str(settings.MODELS_DIR / "whisper")
        os.makedirs(root, exist_ok=True)
        logger.info("Loading Whisper model: %s", model_size)
        _whisper_model = whisper.load_model(model_size, download_root=root)
        _whisper_model_size = model_size
    return _whisper_model


def _get_ffmpeg_exe() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in (
        r"C:\ffmpeg\bin\ffmpeg.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"),
    ):
        if candidate and os.path.isfile(candidate):
            return candidate
    try:
        import imageio_ffmpeg

        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and os.path.isfile(bundled):
            return bundled
    except ImportError:
        pass
    return None


def _ensure_ffmpeg_for_whisper() -> bool:
    """Point Whisper at ffmpeg (system or bundled via imageio-ffmpeg)."""
    exe = _get_ffmpeg_exe()
    if not exe:
        return False

    tools_dir = Path(exe).parent
    os.environ["PATH"] = str(tools_dir) + os.pathsep + os.environ.get("PATH", "")

    if HAS_WHISPER:
        import whisper.audio as whisper_audio

        def _load_audio(file: str, sr: int = whisper_audio.SAMPLE_RATE):
            cmd = [
                exe,
                "-nostdin",
                "-threads",
                "0",
                "-i",
                file,
                "-f",
                "s16le",
                "-ac",
                "1",
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(sr),
                "-",
            ]
            from subprocess import CalledProcessError, run

            try:
                out = run(cmd, capture_output=True, check=True).stdout
            except CalledProcessError as e:
                raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

            import numpy as np

            return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

        whisper_audio.load_audio = _load_audio

    return True


def transcribe(audio_path: str, language: str | None = None, model_size: str = "small") -> dict:
    path = Path(audio_path)
    if not path.exists():
        return {"text": "", "language": "", "duration": 0, "method": "error"}

    if not HAS_WHISPER:
        return {
            "text": (
                "Whisper is not installed. In the backend folder run:\n"
                "  .venv\\Scripts\\pip install openai-whisper\n"
                "Then restart run.cmd"
            ),
            "language": language or "unknown",
            "duration": 0,
            "method": "fallback",
        }

    if not _ensure_ffmpeg_for_whisper():
        return {
            "text": (
                "ffmpeg is required for audio. Run in the backend folder:\n"
                "  .venv\\Scripts\\pip install imageio-ffmpeg openai-whisper\n"
                "Then restart run.cmd"
            ),
            "language": language or "unknown",
            "duration": 0,
            "method": "fallback",
        }

    model = _get_model(model_size)
    if model is None:
        return {
            "text": f"[Could not load Whisper model: {model_size}]",
            "language": language or "unknown",
            "duration": 0,
            "method": "fallback",
        }

    result = model.transcribe(
        str(path),
        language=language,
        verbose=False,
        task="transcribe",
    )
    duration = 0
    if result.get("segments"):
        duration = result["segments"][-1].get("end", 0)

    return {
        "text": result.get("text", "").strip(),
        "language": result.get("language", language or ""),
        "duration": duration,
        "segments": result.get("segments", []),
        "method": f"whisper-{model_size}",
    }
