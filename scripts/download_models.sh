#!/usr/bin/env bash
# Download open-source models (run once). Requires: pip install huggingface_hub
set -e
MODELS_DIR="${MODELS_DIR:-./models}"
mkdir -p "$MODELS_DIR"

echo "Downloading DistilBART summarizer (CPU-friendly)..."
huggingface-cli download sshleifer/distilbart-cnn-12-6 --local-dir "$MODELS_DIR/distilbart-cnn"

echo "Downloading T5 paraphraser..."
huggingface-cli download humarin/chatgpt_paraphraser_on_T5_base --local-dir "$MODELS_DIR/t5-paraphrase"

echo "Downloading Indian language translators (English pairs)..."
for pair in en-hi hi-en en-ta ta-en en-te te-en en-ml ml-en; do
  huggingface-cli download "Helsinki-NLP/opus-mt-${pair}" --local-dir "$MODELS_DIR/opus-mt-${pair}"
done

echo "Downloading MiniLM embeddings..."
huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir "$MODELS_DIR/minilm-l6-v2"

echo "Done. Models stored in $MODELS_DIR"
