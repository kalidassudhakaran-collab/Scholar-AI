def chunk_text(text: str, max_words: int = 900, overlap: int = 50) -> list[str]:
    """Split text into overlapping word chunks."""
    words = text.split()
    if not words:
        return []
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + max_words]
        chunks.append(" ".join(chunk))
        i += max(1, max_words - overlap)
    return chunks


def merge_summaries(summaries: list[str], summarize_fn) -> str:
    """Merge chunk summaries into one final summary."""
    combined = " ".join(summaries)
    if len(combined.split()) <= 900:
        return summarize_fn(combined)
    return merge_summaries(
        [summarize_fn(s) for s in summaries],
        summarize_fn,
    )
