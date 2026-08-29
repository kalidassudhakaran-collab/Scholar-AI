"""Detect likely AI-generated text (offline model + heuristic fallback)."""

import logging
import re
import statistics
import threading

logger = logging.getLogger(__name__)

_classifier = None
_classifier_lock = threading.Lock()
_classifier_unavailable = False

DETECTOR_MODEL = "Hello-SimpleAI/chatgpt-detector-roberta"
CHUNK_CHARS = 1800

AI_PHRASES = (
    "it is important to note",
    "it's important to note",
    "in conclusion",
    "in today's world",
    "delve into",
    "delve deeper",
    "furthermore",
    "moreover",
    "additionally",
    "as an ai",
    "as a language model",
    "utilize",
    "leverage",
    "comprehensive",
    "multifaceted",
    "tapestry",
    "landscape of",
    "plays a crucial role",
    "it is worth noting",
    "in summary",
    "overall,",
    "on the other hand",
    "that being said",
)

TRANSITION_WORDS = (
    "however",
    "therefore",
    "thus",
    "hence",
    "consequently",
    "furthermore",
    "moreover",
    "additionally",
    "nevertheless",
    "nonetheless",
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 8]


def _chunk_text(text: str, size: int = CHUNK_CHARS) -> list[str]:
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            break_at = text.rfind(" ", start + size // 2, end)
            if break_at > start:
                end = break_at
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]


def _ai_label_score(result: list[dict]) -> float:
    """Map classifier output to P(AI-generated)."""
    ai_score = None
    human_score = None
    for item in result:
        label = str(item.get("label", "")).lower()
        score = float(item.get("score", 0))
        if any(x in label for x in ("fake", "chatgpt", "generated", "label_1")) or label == "ai":
            ai_score = score if ai_score is None else max(ai_score, score)
        if "human" in label or "real" in label or label == "label_0":
            human_score = score if human_score is None else max(human_score, score)
    if ai_score is not None:
        return ai_score
    if human_score is not None:
        return 1.0 - human_score
    if result:
        return float(result[0].get("score", 0.5))
    return 0.5


def _get_classifier():
    """Load RoBERTa detector once and reuse (avoids re-download per request)."""
    global _classifier, _classifier_unavailable

    if _classifier_unavailable:
        return None
    if _classifier is not None:
        return _classifier

    from ai_engine.model_registry import HAS_TRANSFORMERS

    if not HAS_TRANSFORMERS:
        return None

    with _classifier_lock:
        if _classifier is not None:
            return _classifier
        if _classifier_unavailable:
            return None
        try:
            from transformers import pipeline

            logger.info("Loading AI detector model: %s", DETECTOR_MODEL)
            _classifier = pipeline(
                "text-classification",
                model=DETECTOR_MODEL,
                truncation=True,
                max_length=512,
                device=-1,
            )
        except Exception as exc:
            logger.warning("AI detector model load failed: %s", exc)
            _classifier_unavailable = True
            return None
    return _classifier


def _classify_chunks(chunks: list[str]) -> tuple[float, list[dict], str]:
    if not chunks:
        return 0.0, [], ""

    classifier = _get_classifier()
    if classifier is None:
        return 0.0, [], ""

    segment_scores = []
    for i, chunk in enumerate(chunks):
        try:
            raw = classifier(chunk[:4000])
            if isinstance(raw, dict):
                raw = [raw]
            prob = _ai_label_score(raw)
            segment_scores.append(
                {
                    "index": i + 1,
                    "ai_probability": round(prob, 3),
                    "preview": chunk[:120] + ("…" if len(chunk) > 120 else ""),
                }
            )
        except Exception as exc:
            logger.warning("Chunk %s classification failed: %s", i, exc)

    if not segment_scores:
        return 0.0, [], ""

    avg = sum(s["ai_probability"] for s in segment_scores) / len(segment_scores)
    return avg, segment_scores, DETECTOR_MODEL


def _heuristic_score(text: str) -> tuple[float, list[str]]:
    signals: list[str] = []
    score = 0.0
    low = text.lower()
    words = re.findall(r"[a-zA-Z']+", low)
    word_count = len(words)

    if word_count < 40:
        signals.append("Text is very short — detection is less reliable.")
        score += 0.1

    phrase_hits = [p for p in AI_PHRASES if p in low]
    if phrase_hits:
        score += min(0.32, len(phrase_hits) * 0.07)
        signals.append(
            "Common AI phrases: "
            + ", ".join(f'"{p}"' for p in phrase_hits[:4])
            + ("…" if len(phrase_hits) > 4 else "")
        )

    sentences = _split_sentences(text)
    if len(sentences) >= 3:
        lengths = [len(s.split()) for s in sentences]
        avg_len = statistics.mean(lengths)
        stdev_len = statistics.stdev(lengths) if len(lengths) > 1 else 0
        cv = stdev_len / avg_len if avg_len else 0
        if cv < 0.28:
            score += 0.18
            signals.append("Very uniform sentence lengths (typical of AI drafting).")
        if 12 <= avg_len <= 22 and cv < 0.35:
            score += 0.08

    if word_count >= 20:
        unique_ratio = len(set(words)) / word_count
        if unique_ratio < 0.42:
            score += 0.14
            signals.append("Low vocabulary variety.")

    trans_count = sum(low.count(f" {tw} ") for tw in TRANSITION_WORDS)
    if word_count and trans_count / word_count > 0.04:
        score += 0.1
        signals.append("High density of formal transition words.")

    return min(1.0, score), signals


def _verdict(ai_prob: float) -> tuple[str, str]:
    pct = ai_prob * 100
    if ai_prob >= 0.72:
        return "Likely AI-generated", "high"
    if ai_prob >= 0.52:
        return "Possibly AI-generated", "medium"
    if ai_prob >= 0.35:
        return "Mixed / uncertain", "low"
    return "Likely human-written", "medium"


def _format_report(
    text: str,
    ai_prob: float,
    verdict: str,
    confidence: str,
    model_used: str,
    segment_scores: list[dict],
    signals: list[str],
) -> str:
    pct = round(ai_prob * 100, 1)
    lines = [
        f"AI detection: {pct}% probability of AI-generated text",
        f"Verdict: {verdict} ({confidence} confidence)",
        f"Method: {model_used}",
        f"Word count: {len(text.split())}",
        "",
    ]
    if signals:
        lines.append("Signals:")
        for s in signals:
            lines.append(f"  - {s}")
        lines.append("")
    if segment_scores:
        lines.append("Segment analysis:")
        for seg in segment_scores[:8]:
            sp = round(seg["ai_probability"] * 100, 1)
            lines.append(f"  [{seg['index']}] {sp}% AI — \"{seg['preview']}\"")
        if len(segment_scores) > 8:
            lines.append(f"  … and {len(segment_scores) - 8} more segments")
        lines.append("")
    lines.append(
        "Note: This is an automated estimate for academic review, not legal proof. "
        "Short texts and heavily edited human writing can be misclassified."
    )
    return "\n".join(lines)


def detect_ai_text(text: str, sensitivity: str = "balanced") -> dict:
    try:
        return _detect_ai_text_impl(text, sensitivity=sensitivity)
    except Exception as exc:
        logger.exception("AI detection failed")
        heuristic_score, signals = _heuristic_score((text or "").strip())
        signals.append(f"Model error (used fallback): {exc}")
        ai_prob = heuristic_score
        verdict, confidence = _verdict(ai_prob)
        return {
            "output_text": _format_report(
                (text or "").strip(),
                ai_prob,
                verdict,
                confidence,
                "heuristic-fallback",
                [],
                signals,
            ),
            "model_used": "heuristic-fallback",
            "ai_probability": round(ai_prob, 4),
            "percentage": round(ai_prob * 100, 1),
            "verdict": verdict,
            "confidence": confidence,
            "segment_scores": [],
            "signals": signals,
        }


def _detect_ai_text_impl(text: str, sensitivity: str = "balanced") -> dict:
    text = (text or "").strip()
    if not text:
        return {
            "output_text": "No text provided.",
            "model_used": "none",
            "ai_probability": 0.0,
            "percentage": 0.0,
            "verdict": "N/A",
            "confidence": "low",
        }

    chunks = _chunk_text(text)
    ml_score, segment_scores, ml_model = _classify_chunks(chunks)
    heuristic_score, signals = _heuristic_score(text)

    if ml_model:
        if sensitivity == "strict":
            ai_prob = 0.85 * ml_score + 0.15 * heuristic_score
        elif sensitivity == "lenient":
            ai_prob = 0.65 * ml_score + 0.35 * heuristic_score
        else:
            ai_prob = 0.75 * ml_score + 0.25 * heuristic_score
        model_used = ml_model
    else:
        ai_prob = heuristic_score
        model_used = "heuristic-fallback"
        signals.append(
            "Neural detector not loaded — using pattern analysis. "
            "For best results: pip install -r requirements-ai.txt and restart run.cmd "
            "(first run downloads ~500 MB)."
        )

    ai_prob = max(0.0, min(1.0, ai_prob))
    verdict, confidence = _verdict(ai_prob)
    pct = round(ai_prob * 100, 1)

    return {
        "output_text": _format_report(
            text, ai_prob, verdict, confidence, model_used, segment_scores, signals
        ),
        "model_used": model_used,
        "ai_probability": round(ai_prob, 4),
        "percentage": pct,
        "verdict": verdict,
        "confidence": confidence,
        "segment_scores": segment_scores,
        "signals": signals,
    }
