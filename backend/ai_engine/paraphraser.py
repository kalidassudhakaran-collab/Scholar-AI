import re

import torch

STYLE_PROMPTS = {
    "fluent": "paraphrase: {text}",
    "formal": "paraphrase formally: {text}",
    "creative": "paraphrase creatively: {text}",
}


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _group_sentences(sentences: list[str], max_words: int = 55) -> list[str]:
    """Group sentences into chunks the T5 paraphraser can handle fully."""
    if not sentences:
        return []
    chunks: list[str] = []
    current: list[str] = []
    count = 0

    for sent in sentences:
        w = len(sent.split())
        if current and count + w > max_words:
            chunks.append(" ".join(current))
            current = [sent]
            count = w
        else:
            current.append(sent)
            count += w

    if current:
        chunks.append(" ".join(current))
    return chunks


def _fallback_paraphrase(text: str, style: str) -> str:
    if not text.strip():
        return "(No input text provided.)"
    return text


def _run_paraphrase(
    model,
    tokenizer,
    chunk: str,
    style: str,
    device: torch.device,
) -> str:
    prompt = STYLE_PROMPTS[style].format(text=chunk)
    chunk_words = len(chunk.split())
    max_new_tokens = min(256, max(64, chunk_words * 2 + 20))

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    gen_kwargs = {
        "max_new_tokens": max_new_tokens,
        "num_beams": 4,
        "do_sample": False,
        "length_penalty": 1.1,
        "no_repeat_ngram_size": 3,
    }
    if style == "creative":
        gen_kwargs = {
            "max_new_tokens": max_new_tokens,
            "do_sample": True,
            "temperature": 0.9,
            "top_p": 0.92,
            "no_repeat_ngram_size": 3,
        }

    with torch.no_grad():
        ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            **gen_kwargs,
        )
    return tokenizer.decode(ids[0], skip_special_tokens=True).strip()


def paraphrase(text: str, style: str = "fluent") -> dict:
    text = (text or "").strip()
    if not text:
        return {"output_text": "(No input text provided.)", "model_used": "none"}

    style = style if style in STYLE_PROMPTS else "fluent"

    from ai_engine.model_registry import HAS_TRANSFORMERS, ModelRegistry

    loaded = ModelRegistry.get_instance().get_paraphraser()
    if loaded is None or not HAS_TRANSFORMERS:
        return {"output_text": _fallback_paraphrase(text, style), "model_used": "fallback"}

    model, tokenizer = loaded
    device = next(model.parameters()).device
    word_count = len(text.split())

    if word_count <= 55:
        chunks = [text]
    else:
        chunks = _group_sentences(_split_sentences(text), max_words=55)

    parts = [_run_paraphrase(model, tokenizer, c, style, device) for c in chunks]
    output = " ".join(parts)

    model_name = getattr(model.config, "_name_or_path", "t5-paraphrase")
    return {"output_text": output, "model_used": str(model_name), "style": style}
