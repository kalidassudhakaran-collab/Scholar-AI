import logging

logger = logging.getLogger(__name__)

# Indian languages: English, Hindi, Tamil, Telugu, Malayalam
SUPPORTED_PAIRS = {
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("en", "ta"): "Helsinki-NLP/opus-mt-en-ta",
    ("ta", "en"): "Helsinki-NLP/opus-mt-ta-en",
    ("en", "te"): "Helsinki-NLP/opus-mt-en-te",
    ("te", "en"): "Helsinki-NLP/opus-mt-te-en",
    ("en", "ml"): "Helsinki-NLP/opus-mt-en-ml",
    ("ml", "en"): "Helsinki-NLP/opus-mt-ml-en",
}

LANGUAGE_LABELS = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
}

INDIAN_LANGUAGE_CODES = frozenset(LANGUAGE_LABELS.keys())


def get_model_id_for_pair(src: str, tgt: str) -> str:
    src, tgt = src.lower(), tgt.lower()
    if (src, tgt) not in SUPPORTED_PAIRS:
        raise ValueError(
            f"Unsupported language pair: {src} → {tgt}. "
            f"Supported languages: {', '.join(LANGUAGE_LABELS.values())}."
        )
    return SUPPORTED_PAIRS[(src, tgt)]


def _translate_online(text: str, src: str, tgt: str) -> dict | None:
    """Lightweight translation via Google (needs internet). No model download."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        return None

    def translate_chunk(chunk: str, s: str, t: str) -> str:
        if not chunk.strip():
            return chunk
        return GoogleTranslator(source=s, target=t).translate(chunk)

    max_len = 4500
    chunks = [text[i : i + max_len] for i in range(0, len(text), max_len)] or [text]
    try:
        parts = [translate_chunk(c, src, tgt) for c in chunks]
    except Exception as e:
        logger.warning("Online translation failed: %s", e)
        return None

    return {
        "output_text": " ".join(parts),
        "model_used": "google-translate-online",
        "source_language": src,
        "target_language": tgt,
        "word_count": len(text.split()),
    }


def _translate_offline_model(text: str, src: str, tgt: str) -> dict | None:
    """Helsinki MarianMT when transformers + models are installed."""
    from ai_engine.model_registry import HAS_TRANSFORMERS, ModelRegistry

    if not HAS_TRANSFORMERS:
        return None

    model_id = get_model_id_for_pair(src, tgt)
    try:
        tokenizer, model = ModelRegistry.get_instance().get_translation_model(src, tgt)
    except Exception as e:
        logger.warning("Could not load model %s: %s", model_id, e)
        return None

    max_chars = 4000
    chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)] or [text]
    outputs = []

    import torch

    device = next(model.parameters()).device  # noqa: F841 — used via .to(device)
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            translated = model.generate(**inputs, max_length=512)
        outputs.append(tokenizer.decode(translated[0], skip_special_tokens=True))

    return {
        "output_text": " ".join(outputs),
        "model_used": model_id,
        "source_language": src,
        "target_language": tgt,
        "word_count": len(text.split()),
    }


def _translate_direct(text: str, src: str, tgt: str) -> dict:
    # 1) Offline models (best when installed)
    result = _translate_offline_model(text, src, tgt)
    if result:
        return result

    # 2) Online fallback (works out of the box with internet)
    result = _translate_online(text, src, tgt)
    if result:
        return result

    # 3) Nothing available
    src_label = LANGUAGE_LABELS.get(src, src)
    tgt_label = LANGUAGE_LABELS.get(tgt, tgt)
    return {
        "output_text": (
            f"Translation unavailable. Run in backend folder:\n"
            f"  pip install deep-translator\n"
            f"Then restart the server. ({src_label} → {tgt_label})\n\n"
            f"Original text:\n{text[:500]}"
        ),
        "model_used": "unavailable",
        "source_language": src,
        "target_language": tgt,
        "word_count": len(text.split()),
    }


def translate(text: str, source_lang: str, target_lang: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {"output_text": "", "model_used": "none", "word_count": 0}

    src, tgt = source_lang.lower(), target_lang.lower()

    if src not in INDIAN_LANGUAGE_CODES or tgt not in INDIAN_LANGUAGE_CODES:
        raise ValueError(
            f"Unknown language. Choose from: {', '.join(f'{k} ({v})' for k, v in LANGUAGE_LABELS.items())}"
        )

    if src == tgt:
        return {
            "output_text": text,
            "model_used": "none",
            "source_language": src,
            "target_language": tgt,
            "word_count": len(text.split()),
        }

    if (src, tgt) in SUPPORTED_PAIRS:
        return _translate_direct(text, src, tgt)

    if src != "en" and tgt != "en":
        via_en = _translate_direct(text, src, "en")
        result = _translate_direct(via_en["output_text"], "en", tgt)
        result["model_used"] = f"{via_en['model_used']} + {result['model_used']}"
        result["source_language"] = src
        result["target_language"] = tgt
        result["via_english"] = True
        return result

    raise ValueError(f"Cannot translate {src} → {tgt}")
