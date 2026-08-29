import re

from ai_engine.paraphraser import paraphrase

AI_PHRASES = {
    "it is important to note that": "notably,",
    "it is important to note": "notably,",
    "in conclusion,": "to sum up,",
    "in conclusion": "to sum up,",
    "utilize": "use",
    "utilizing": "using",
    "leverage": "use",
    "delve into": "explore",
    "delve": "explore",
    "crucially,": "",
    "crucially": "",
    "furthermore,": "also,",
    "furthermore": "also,",
    "in order to": "to",
    "a wide range of": "many",
    "plays a crucial role": "matters",
    "it is worth noting": "note that",
}

TRANSITIONS = ("However,", "Moreover,", "In fact,", "Interestingly,", "That said,")


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _replace_ai_phrases(text: str) -> str:
    out = text
    for phrase, replacement in sorted(AI_PHRASES.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        out = pattern.sub(replacement, out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()


def _vary_structure(sentences: list[str], style: str) -> list[str]:
    if len(sentences) < 2:
        return sentences

    out = [sentences[0]]
    for i, sent in enumerate(sentences[1:], start=1):
        if i % 3 == 0 and not sent.startswith(TRANSITIONS):
            trans = TRANSITIONS[i % len(TRANSITIONS)]
            sent = f"{trans} {sent[0].lower() + sent[1:]}" if sent else sent
        if style == "academic" and sent.lower().startswith("also,"):
            sent = "Additionally, " + sent[5:].lstrip()
        out.append(sent)
    return out


def humanize(text: str, style: str = "natural") -> dict:
    text = (text or "").strip()
    if not text:
        return {"output_text": "(No input text provided.)", "model_used": "none", "style": style}

    style = style if style in ("natural", "academic", "casual") else "natural"

    layer1 = _replace_ai_phrases(text)
    sentences = _vary_structure(_split_sentences(layer1), style)
    combined = " ".join(sentences)

    # Academic: rule-based only (fast, keeps formal tone)
    if style == "academic":
        return {
            "output_text": combined,
            "model_used": "rule-based-humanizer",
            "style": style,
        }

    para_style = "creative" if style == "casual" else "fluent"
    result = paraphrase(combined, style=para_style)

    if result.get("model_used") in ("fallback", "none"):
        return {
            "output_text": combined,
            "model_used": "rule-based-humanizer",
            "style": style,
        }

    return {
        "output_text": result["output_text"],
        "model_used": "humanizer",
        "style": style,
    }
