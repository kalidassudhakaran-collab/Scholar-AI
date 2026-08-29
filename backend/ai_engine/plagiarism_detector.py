import re
from difflib import SequenceMatcher

logger = __import__("logging").getLogger(__name__)

LEXICAL_THRESHOLD = 0.82  # copy-paste / near-duplicate wording
SEMANTIC_THRESHOLD = 0.58  # paraphrased meaning (MiniLM scores ~0.55–0.75)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 10]


def _lexical_best(sentence: str, candidates: list[str]) -> tuple[float, int, str]:
    best_score, best_idx, best_text = 0.0, -1, ""
    low = sentence.lower()
    for j, cand in enumerate(candidates):
        score = SequenceMatcher(None, low, cand.lower()).ratio()
        if score > best_score:
            best_score, best_idx, best_text = score, j, cand
    return best_score, best_idx, best_text


def _semantic_check(
    sentences_a: list[str], sentences_b: list[str], threshold: float
) -> list[dict] | None:
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        return None

    try:
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        emb_a = model.encode(sentences_a, show_progress_bar=False)
        emb_b = model.encode(sentences_b, show_progress_bar=False)
        # Cosine similarity without sklearn
        norm_a = np.linalg.norm(emb_a, axis=1, keepdims=True) + 1e-9
        norm_b = np.linalg.norm(emb_b, axis=1, keepdims=True) + 1e-9
        sim = (emb_a / norm_a) @ (emb_b / norm_b).T
    except Exception as exc:
        logger.warning("Semantic plagiarism check failed: %s", exc)
        return None

    matches = []
    used_b: set[int] = set()
    for i, row in enumerate(sim):
        order = np.argsort(-row)
        for j in order:
            j = int(j)
            score = float(row[j])
            if score >= threshold and j not in used_b:
                matches.append(
                    {
                        "original_sentence": sentences_a[i],
                        "matching_sentence": sentences_b[j],
                        "similarity_score": round(score, 3),
                        "sentence_index_a": i,
                        "sentence_index_b": j,
                    }
                )
                used_b.add(j)
                break
    return matches


def _format_report(
    text_a: str,
    text_b: str,
    matches: list[dict],
    percentage: float,
    model_used: str,
    threshold: float,
) -> str:
    lines = [
        f"Plagiarism scan: {percentage}% of sentences in Document A match Document B",
        f"Method: {model_used} (threshold {threshold:.0%} similarity)",
        f"Matched sentences: {len(matches)} / {max(len(_split_sentences(text_a)), 1)}",
        "",
    ]
    if not matches:
        lines.append("No strong matches found at the current threshold.")
        return "\n".join(lines)

    lines.append("Flagged matches:")
    for i, m in enumerate(matches[:25], 1):
        lines.append(f"\n{i}. Similarity {m['similarity_score']:.0%}")
        lines.append(f"   A: {m['original_sentence'][:200]}")
        lines.append(f"   B: {m['matching_sentence'][:200]}")
    if len(matches) > 25:
        lines.append(f"\n... and {len(matches) - 25} more matches.")
    return "\n".join(lines)


def check_plagiarism(
    text_a: str,
    text_b: str,
    threshold: float | None = None,
) -> dict:
    text_a = (text_a or "").strip()
    text_b = (text_b or "").strip()
    if not text_a or not text_b:
        return {
            "output_text": "Provide both documents to compare.",
            "model_used": "none",
            "percentage": 0.0,
            "matches": [],
        }

    sentences_a = _split_sentences(text_a)
    sentences_b = _split_sentences(text_b)
    if not sentences_a:
        sentences_a = [text_a]
    if not sentences_b:
        sentences_b = [text_b]

    sem_threshold = threshold if threshold is not None else SEMANTIC_THRESHOLD
    lex_threshold = threshold if threshold is not None else LEXICAL_THRESHOLD

    matches = _semantic_check(sentences_a, sentences_b, sem_threshold)
    model_used = "minilm-semantic"
    used_threshold = sem_threshold

    if matches is None:
        model_used = "lexical-sequence"
        used_threshold = lex_threshold
        matches = []
        used_b: set[int] = set()
        for i, sent in enumerate(sentences_a):
            score, j, match_text = _lexical_best(sent, sentences_b)
            if score >= lex_threshold and j not in used_b:
                matches.append(
                    {
                        "original_sentence": sent,
                        "matching_sentence": match_text,
                        "similarity_score": round(score, 3),
                        "sentence_index_a": i,
                        "sentence_index_b": j,
                    }
                )
                used_b.add(j)

    total = max(len(sentences_a), 1)
    percentage = round(len(matches) / total * 100, 1)
    report = _format_report(text_a, text_b, matches, percentage, model_used, used_threshold)

    return {
        "output_text": report,
        "model_used": model_used,
        "percentage": percentage,
        "matches": matches,
        "total_sentences": len(sentences_a),
        "matched_sentences": len(matches),
    }
