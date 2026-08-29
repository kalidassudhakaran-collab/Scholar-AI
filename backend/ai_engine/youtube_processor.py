import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

YOUTUBE_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})"
)


def extract_video_id(url: str) -> str | None:
    match = YOUTUBE_RE.search(url)
    return match.group(1) if match else None


def get_transcript(video_id: str) -> str | None:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        langs = ("en", "en-US", "hi", "ml", "ta", "te")
        try:
            fetched = api.fetch(video_id, languages=langs)
        except Exception:
            transcript_list = api.list(video_id)
            fetched = next(iter(transcript_list)).fetch()

        return " ".join(snippet.text.replace("\n", " ") for snippet in fetched).strip()
    except Exception as e:
        logger.info("Caption fetch failed for %s: %s", video_id, e)
        return None


def download_audio(url: str, output_dir: str) -> str | None:
    try:
        import yt_dlp
        from ai_engine.speech_processor import _get_ffmpeg_exe

        ffmpeg = _get_ffmpeg_exe()
        opts = {
            "format": "worstaudio/worst",
            "outtmpl": f"{output_dir}/%(id)s.%(ext)s",
            "quiet": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "64"}
            ],
        }
        if ffmpeg:
            opts["ffmpeg_location"] = str(Path(ffmpeg).parent)
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid = info["id"]
            return f"{output_dir}/{vid}.mp3"
    except Exception as e:
        logger.warning("Audio download failed: %s", e)
        return None


def process(url: str, summarize_fn=None) -> dict:
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL", "transcript": "", "summary": ""}

    transcript = get_transcript(video_id)

    if not transcript:
        import tempfile

        from ai_engine.speech_processor import transcribe

        tmp = tempfile.mkdtemp()
        audio_path = download_audio(url, tmp)
        if audio_path:
            tr = transcribe(audio_path)
            transcript = tr.get("text", "")
        else:
            transcript = "[Could not fetch captions or download audio]"

    word_count = len(transcript.split()) if transcript else 0
    is_short = word_count < 120

    summary = ""
    if not transcript:
        summary = ""
    elif is_short:
        summary = (
            "This video is very short, so the full caption text is shown below "
            "instead of an AI rewrite."
        )
    elif summarize_fn:
        summary = summarize_fn(transcript)
    else:
        words = transcript.split()
        summary = " ".join(words[:150]) + ("…" if len(words) > 150 else "")

    key_points = []
    if transcript and not is_short:
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", transcript)
            if len(s.strip()) > 30
        ]
        step = max(1, len(sentences) // 6)
        for i in range(0, len(sentences), step):
            key_points.append(sentences[i])
            if len(key_points) >= 6:
                break
    elif transcript:
        key_points = [transcript]

    return {
        "video_id": video_id,
        "url": url,
        "transcript": transcript,
        "summary": summary,
        "key_points": key_points,
    }
