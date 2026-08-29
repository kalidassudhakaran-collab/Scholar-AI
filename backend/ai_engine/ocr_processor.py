import logging
import os
import re
import shutil
from pathlib import Path


def _fix_ocr_glue(text: str) -> str:
    """Fix common Tesseract merges like 'factsand' -> 'facts and'."""
    text = re.sub(r"([a-z]{2,})(and|or|the|to|of|in)\b", r"\1 \2", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text)

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image

    HAS_TESSERACT = True
    _tesseract = shutil.which("tesseract")
    if not _tesseract:
        for candidate in (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ):
            if os.path.isfile(candidate):
                _tesseract = candidate
                break
    if _tesseract:
        pytesseract.pytesseract.tesseract_cmd = _tesseract
except ImportError:
    HAS_TESSERACT = False

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def _ocr_image_pillow(image_path: str) -> dict:
    if not HAS_TESSERACT:
        return {
            "text": f"[OCR unavailable — install tesseract & pytesseract for: {image_path}]",
            "method": "fallback",
            "confidence": 0,
        }
    img = Image.open(image_path).convert("RGB")
    if max(img.size) < 1400:
        scale = 1400 / max(img.size)
        img = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            Image.Resampling.LANCZOS,
        )

    config = "--psm 6 -c preserve_interword_spaces=1"
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=config)

    line_words: dict[tuple, list[str]] = {}
    confs: list[int] = []
    for i, word in enumerate(data["text"]):
        w = (word or "").strip()
        if not w:
            continue
        conf = int(float(data["conf"][i]))
        if conf <= 0:
            continue
        confs.append(conf)
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        line_words.setdefault(key, []).append(w)

    text = "\n".join(" ".join(line_words[k]) for k in sorted(line_words.keys()))
    if not text.strip():
        text = pytesseract.image_to_string(img, config=config).strip()

    text = _fix_ocr_glue(text.strip())
    avg_conf = sum(confs) / len(confs) if confs else 0
    return {"text": text, "method": "tesseract", "confidence": avg_conf}


def process_image(file_path: str) -> dict:
    result = _ocr_image_pillow(file_path)
    return {
        "full_text": result["text"],
        "method": result["method"],
        "confidence": result.get("confidence", 0),
    }


def process_pdf(file_path: str) -> dict:
    if not HAS_PDFPLUMBER:
        return {
            "full_text": "[PDF processing requires pdfplumber]",
            "pages": [],
            "method": "fallback",
        }

    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            method = "digital" if len(text.strip()) > 50 else "ocr_needed"
            pages.append({"page": i + 1, "text": text.strip(), "method": method})

    full_text = "\n\n".join(p["text"] for p in pages if p["text"])
    if not full_text.strip():
        full_text = "[Scanned PDF — install tesseract for OCR on rendered pages]"

    return {"full_text": full_text, "pages": pages, "method": "pdfplumber"}


def process_file(file_path: str) -> dict:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return process_pdf(str(path))
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}:
        return process_image(str(path))
    if suffix == ".txt":
        return {"full_text": path.read_text(encoding="utf-8", errors="replace"), "method": "plain"}
    return {"full_text": f"Unsupported file type: {suffix}", "method": "unsupported"}
