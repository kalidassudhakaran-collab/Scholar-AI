import re
from collections import Counter

import torch

from ai_engine.model_registry import HAS_TRANSFORMERS, ModelRegistry
from ai_engine.utils.text_chunker import chunk_text, merge_summaries

SUMMARY_LENGTHS = {
    "short": {"max_new_tokens": 64, "min_new_tokens": 20, "sentences": 2},
    "detailed": {"max_new_tokens": 160, "min_new_tokens": 50, "sentences": 4},
    "bullets": {"max_new_tokens": 120, "min_new_tokens": 30, "sentences": 5},
}

_STOP = frozenset(
    "a an the and or but in on at to for of is are was were be been being "
    "that this it as with by from they their we our you your not".split()
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _sentence_words(sentence: str) -> list[str]:
    return [w.lower() for w in re.findall(r"\w+", sentence) if w.lower() not in _STOP]


def _pick_sentences(sentences: list[str], n: int) -> list[str]:
    """Score sentences by term importance; return top N in original order."""
    if len(sentences) <= n:
        return sentences

    word_freq: Counter = Counter()
    per_sent_words = []
    for s in sentences:
        ws = _sentence_words(s)
        per_sent_words.append(ws)
        word_freq.update(ws)

    scored = []
    for i, (s, ws) in enumerate(zip(sentences, per_sent_words)):
        if not ws:
            score = 0.0
        else:
            score = sum(word_freq[w] for w in ws) / len(ws)
        score += 0.15 / (i + 1)  # slight preference for early context
        scored.append((score, i, s))

    top = sorted(scored, key=lambda x: -x[0])[:n]
    top.sort(key=lambda x: x[1])
    return [s for _, _, s in top]


def _extractive_summarize(text: str, summary_type: str) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return text.strip() or "(No input text provided.)"

    cfg = SUMMARY_LENGTHS.get(summary_type, SUMMARY_LENGTHS["detailed"])
    n = min(cfg["sentences"], len(sentences))
    chosen = _pick_sentences(sentences, n)

    if summary_type == "bullets":
        return "\n".join(f"- {s}" for s in chosen)

    return " ".join(chosen)


def _is_incomplete(output: str) -> bool:
    text = output.strip()
    if not text:
        return True
    if text[-1] not in ".!?":
        return True
    if text.endswith((" on", " the", " a", " an", " to", " of", " and", " or")):
        return True
    return False


def _is_echo(output: str, source: str) -> bool:
    out = output.strip().lower()
    src = source.strip().lower()
    if not out or not src:
        return True
    if len(out.split()) > len(src.split()) * 0.72:
        return True
    if src.startswith(out[: min(len(out), 120)]):
        return True
    return False


def _run_seq2seq(model, tokenizer, text: str, max_new_tokens: int, min_new_tokens: int) -> str:
    device = next(model.parameters()).device
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            do_sample=False,
            num_beams=4,
            length_penalty=1.0,
            no_repeat_ngram_size=3,
            early_stopping=True,
        )
    return tokenizer.decode(ids[0], skip_special_tokens=True)


def summarize(text: str, summary_type: str = "detailed", max_length: int | None = None) -> dict:
    text = (text or "").strip()
    if not text:
        return {"output_text": "(No input text provided.)", "model_used": "none"}

    summary_type = summary_type if summary_type in SUMMARY_LENGTHS else "detailed"
    lengths = SUMMARY_LENGTHS[summary_type]
    word_count = len(text.split())

    extractive = _extractive_summarize(text, summary_type)

    # Short passages: smart sentence ranking beats CNN on small inputs
    if word_count < 175:
        return {"output_text": extractive, "model_used": "extractive-smart"}

    loaded = ModelRegistry.get_instance().get_summarizer()
    if loaded is None or not HAS_TRANSFORMERS:
        return {"output_text": extractive, "model_used": "extractive-smart"}

    model, tokenizer = loaded
    max_tokens = max_length or lengths["max_new_tokens"]
    min_tokens = lengths["min_new_tokens"]

    def summarize_chunk(chunk: str) -> str:
        return _run_seq2seq(model, tokenizer, chunk, max_tokens, min_tokens)

    try:
        if word_count > 900:
            chunks = chunk_text(text)
            partials = [summarize_chunk(c) for c in chunks]
            output = merge_summaries(partials, summarize_chunk)
        else:
            output = summarize_chunk(text)
    except Exception:
        return {"output_text": extractive, "model_used": "extractive-smart"}

    if _is_echo(output, text) or _is_incomplete(output):
        return {"output_text": extractive, "model_used": "extractive-smart"}

    if summary_type == "bullets":
        sentences = _split_sentences(output)
        if len(sentences) > 1:
            output = "\n".join(f"- {s}" for s in sentences)
        else:
            output = _extractive_summarize(text, "bullets")

    model_name = getattr(model.config, "_name_or_path", "distilbart-cnn")
    return {"output_text": output, "model_used": str(model_name)}
