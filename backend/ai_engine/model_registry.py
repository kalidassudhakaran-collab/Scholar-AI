import logging
import os
import threading
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, MarianMTModel, MarianTokenizer

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    torch = None


def _device() -> str:
    if not HAS_TRANSFORMERS:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _resolve_path(local_name: str, hf_id: str) -> str:
    local = Path(settings.MODELS_DIR) / local_name
    if local.exists() and any(local.iterdir()):
        return str(local)
    return hf_id


class ModelRegistry:
    """Thread-safe lazy-loading model cache."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._models: dict = {}
        self._device = _device()

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_summarizer(self):
        """Returns (model, tokenizer) for seq2seq summarization."""
        if not HAS_TRANSFORMERS:
            return None
        key = "summarizer"
        if key not in self._models:
            with self._lock:
                if key not in self._models:
                    model_id = _resolve_path(
                        "distilbart-cnn",
                        os.environ.get(
                            "SUMMARIZER_MODEL",
                            "sshleifer/distilbart-cnn-12-6",
                        ),
                    )
                    logger.info("Loading summarizer: %s", model_id)
                    tokenizer = AutoTokenizer.from_pretrained(model_id)
                    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
                    model.to(self._device)
                    model.eval()
                    self._models[key] = (model, tokenizer)
        return self._models[key]

    def get_paraphraser(self):
        """Returns (model, tokenizer) for T5 paraphrasing."""
        if not HAS_TRANSFORMERS:
            return None
        key = "paraphraser"
        if key not in self._models:
            with self._lock:
                if key not in self._models:
                    model_id = _resolve_path(
                        "t5-paraphrase",
                        os.environ.get(
                            "PARAPHRASE_MODEL",
                            "humarin/chatgpt_paraphraser_on_T5_base",
                        ),
                    )
                    logger.info("Loading paraphraser: %s", model_id)
                    tokenizer = AutoTokenizer.from_pretrained(model_id)
                    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
                    model.to(self._device)
                    model.eval()
                    self._models[key] = (model, tokenizer)
        return self._models[key]

    def get_translation_model(self, src: str, tgt: str):
        if not HAS_TRANSFORMERS:
            return None
        from ai_engine.translator import get_model_id_for_pair

        model_id = get_model_id_for_pair(src, tgt)
        key = f"translate:{src}:{tgt}:{model_id}"
        if key not in self._models:
            with self._lock:
                if key not in self._models:
                    local_name = model_id.split("/")[-1]
                    path = _resolve_path(local_name, model_id)
                    logger.info("Loading translator: %s", path)
                    tokenizer = MarianTokenizer.from_pretrained(path)
                    model = MarianMTModel.from_pretrained(path)
                    model.to(self._device)
                    model.eval()
                    self._models[key] = (tokenizer, model)
        return self._models[key]

    # Backward-compatible alias
    def get_summarization_pipeline(self):
        return self.get_summarizer()

    def get_paraphrase_pipeline(self):
        return self.get_paraphraser()
