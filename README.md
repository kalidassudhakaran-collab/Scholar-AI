COdeTEch Intern ID:CITS8123
# Scholar AI

AI-powered academic productivity platform — summarizer, translator, paraphraser, OCR, voice-to-text, YouTube summaries, and more. Offline-first with local open-source models.

## Quick start

### Without Docker (Windows — easiest)

1. Install **Python 3.10+** from [python.org](https://www.python.org/downloads/) — check **“Add python.exe to PATH”**.
2. One command in Command Prompt:

   ```cmd
   cd /d "c:\dev\from scratch\Scholar AI" && run.cmd
   ```

3. Open **http://localhost:8000** (browser may open automatically).

**Frontend:** plain **HTML + CSS + JavaScript** in the `web/` folder — **no Node.js/npm required**. Django serves the pages and the API on the same port.

Uses **SQLite** and in-process AI tasks — no PostgreSQL, Redis, Docker, or Celery worker.

*(The `frontend/` Next.js app is optional and no longer needed for daily use.)*

### With Docker

1. Copy environment file:

   ```cmd
   copy /Y .env.example .env
   ```

2. Start services:

   ```cmd
   docker compose up --build
   ```

3. Open the app:

   - Frontend: http://localhost:3000
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - MinIO console: http://localhost:9001

## Project structure

| Path | Description |
|------|-------------|
| `backend/` | Django REST API, Celery workers, AI engine |
| `frontend/` | Next.js 14 dashboard |
| `models/` | Downloaded HuggingFace models (gitignored) |
| `scripts/` | Model download and utilities |

See [scholar_ai_dev_plan.md](./scholar_ai_dev_plan.md) for the full architecture and roadmap.

## Development (without Docker)

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Requires PostgreSQL and Redis running locally (or use Docker only for `db` and `redis`).

### Phase 1 — Core text features (current)

- **Summarizer** — short / detailed / bullets (DistilBART, with fallback if models missing)
- **Translator** — EN ↔ FR, ES, DE, ZH, AR (Helsinki-NLP MarianMT)
- **Paraphraser** — fluent / formal / creative (T5)
- Celery workers + WebSocket progress + history star/delete

Download models (optional, improves quality):

```bash
bash scripts/download_models.sh
```

Run Celery worker separately when not using Docker:

```bash
celery -A config worker -Q ai,default,files -l info
```

### Phase 2 — Media features (current)

- **OCR** — PDF text extraction + Tesseract for images
- **Voice** — Whisper transcription from uploaded audio
- **YouTube** — captions via API, audio fallback, then summarization

## License

MIT (application code). AI models have their own licenses — see the dev plan.
