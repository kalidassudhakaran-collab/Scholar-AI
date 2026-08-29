# Scholar AI — Complete Development Plan
### AI-Powered Academic Productivity Web Application
**Version 1.0 | Prepared for Cursor AI Implementation**

---

## TABLE OF CONTENTS

1. [Project Overview & Vision](#1-project-overview--vision)
2. [Full Software Architecture](#2-full-software-architecture)
3. [Recommended Tech Stack](#3-recommended-tech-stack)
4. [Recommended AI Models Per Feature](#4-recommended-ai-models-per-feature)
5. [Complete Folder Structure](#5-complete-folder-structure)
6. [Database Schema Design](#6-database-schema-design)
7. [Authentication & Authorization System](#7-authentication--authorization-system)
8. [API Structure](#8-api-structure)
9. [Backend Workflow](#9-backend-workflow)
10. [AI Processing Pipeline](#10-ai-processing-pipeline)
11. [Offline Model Integration Strategy](#11-offline-model-integration-strategy)
12. [User History Management Architecture](#12-user-history-management-architecture)
13. [File Upload System](#13-file-upload-system)
14. [Async / Background Task Processing](#14-async--background-task-processing)
15. [OCR Pipeline Architecture](#15-ocr-pipeline-architecture)
16. [Voice-to-Text Pipeline](#16-voice-to-text-pipeline)
17. [YouTube Processing Workflow](#17-youtube-processing-workflow)
18. [Humanizer Implementation Strategy](#18-humanizer-implementation-strategy)
19. [Plagiarism Detection Strategy](#19-plagiarism-detection-strategy)
20. [Deployment Architecture](#20-deployment-architecture)
21. [Docker Setup](#21-docker-setup)
22. [CI/CD Suggestions](#22-cicd-suggestions)
23. [GPU / RAM / Storage Requirements](#23-gpu--ram--storage-requirements)
24. [Performance Optimization](#24-performance-optimization)
25. [Caching Strategy](#25-caching-strategy)
26. [Security Best Practices](#26-security-best-practices)
27. [Admin Dashboard Requirements](#27-admin-dashboard-requirements)
28. [Scalable Enterprise Architecture](#28-scalable-enterprise-architecture)
29. [Future Upgrade Roadmap](#29-future-upgrade-roadmap)
30. [MVP Roadmap & Development Phases](#30-mvp-roadmap--development-phases)
31. [Production Hosting Recommendations](#31-production-hosting-recommendations)
32. [Open-Source AI Models Reference](#32-open-source-ai-models-reference)
33. [Database Optimization Methods](#33-database-optimization-methods)
34. [Module Interaction Map](#34-module-interaction-map)
35. [Speed & Accuracy Improvement Tips](#35-speed--accuracy-improvement-tips)
36. [Cursor AI Prompt Guide](#36-cursor-ai-prompt-guide)
37. [Summary: Recommended Development Order](#37-summary-recommended-development-order)

---

## 1. Project Overview & Vision

Scholar AI is a **unified, AI-powered academic productivity platform** targeting students, researchers, educators, and academic writers. The goal is to replace 8–10 separate tools with one coherent platform that works offline, costs nearly nothing to run, and stores all AI activity in a searchable history.

### Core Design Principles

- **Offline-first AI**: Run models locally using ONNX, llama.cpp, or Transformers.js — no paid API calls for core features.
- **Modular architecture**: Every feature (OCR, translator, summarizer, etc.) is a standalone Django app or FastAPI router so modules can be added or removed cleanly.
- **History-as-a-feature**: Every AI operation is automatically saved with input, output, timestamp, and metadata. Users can search, re-run, export, and build on past work.
- **Progressive Enhancement**: The app works on any device. Rich features are enhanced on desktop/GPU systems.
- **Low cost**: The entire stack — including hosting — can be run for under $20/month using free-tier services and self-hosted models.

---

## 2. Full Software Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  CLIENT BROWSER                      │
│         Next.js 14 (React 18 + TypeScript)          │
│   ┌──────────┐ ┌──────────┐ ┌────────────────────┐  │
│   │  Pages   │ │Components│ │  State (Zustand)   │  │
│   └──────────┘ └──────────┘ └────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS / WebSocket
┌──────────────────────▼──────────────────────────────┐
│                NGINX REVERSE PROXY                   │
│         (SSL termination, static files, rate limit) │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
┌──────────▼──────┐    ┌──────────▼──────────────────┐
│  Django REST    │    │   Celery Worker (AI Tasks)   │
│  Framework API  │    │   ┌──────────────────────┐   │
│  (Auth, CRUD,   │    │   │ AI Processing Modules │   │
│  File Mgmt,     │    │   │ - Summarizer          │   │
│  History)       │    │   │ - Paraphraser         │   │
│                 │    │   │ - Translator           │   │
│  Django Channels│    │   │ - OCR                 │   │
│  (WebSockets)   │    │   │ - Voice-to-Text        │   │
└──────────┬──────┘    │   │ - Plagiarism           │   │
           │           │   │ - Humanizer            │   │
           │           │   └──────────────────────┘   │
           │           └──────────┬───────────────────┘
           │                      │
┌──────────▼──────────────────────▼───────────────────┐
│              SHARED INFRASTRUCTURE                   │
│  ┌────────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │ PostgreSQL │ │  Redis   │ │  MinIO / S3        │  │
│  │ (main DB)  │ │(cache,   │ │  (file storage)    │  │
│  │            │ │ broker,  │ │                    │  │
│  │            │ │ sessions)│ │                    │  │
│  └────────────┘ └──────────┘ └────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Architecture Decisions & Rationale

**Why Django + FastAPI hybrid?**
Use Django REST Framework as the primary backend for its excellent ORM, admin panel, authentication, and ecosystem. Optionally add FastAPI as a separate AI microservice for heavy model inference — FastAPI handles async natively and is faster for pure API endpoints. Start with Django-only for simplicity.

**Why Next.js 14?**
Server-side rendering for SEO and fast initial loads. App Router for file-based routing. React Server Components to reduce client JavaScript. Built-in API routes for lightweight backend-for-frontend patterns.

**Why Celery + Redis?**
AI tasks (transcription, summarization, OCR) can take 5–60 seconds. Running these synchronously would block the HTTP request. Celery queues tasks in Redis, a worker processes them in the background, and the result is pushed to the client via WebSocket (Django Channels). This is standard, battle-tested, and scales horizontally.

---

## 3. Recommended Tech Stack

### Frontend

| Layer | Technology | Reason |
|---|---|---|
| Framework | Next.js 14 (TypeScript) | SSR, file routing, excellent DX |
| UI Library | shadcn/ui + Tailwind CSS | Customizable components, no lock-in |
| State Management | Zustand | Lightweight, no boilerplate |
| Data Fetching | TanStack Query (React Query) | Caching, background refetch, optimistic updates |
| Forms | React Hook Form + Zod | Type-safe, performant |
| Rich Text | TipTap Editor | Extensible ProseMirror wrapper |
| File Upload | react-dropzone | Drag-and-drop, multi-file |
| Charts | Recharts | Usage history visualizations |
| Icons | Lucide React | Clean, consistent |
| Animations | Framer Motion | Page transitions, micro-interactions |
| Audio Recording | MediaRecorder API (native) + wavesurfer.js | Waveform visualization |
| YouTube Input | Simple URL input + yt-dlp (backend) | No frontend YouTube dependency |

### Backend (Primary — Django)

| Layer | Technology | Reason |
|---|---|---|
| Framework | Django 5.x + Django REST Framework | Battle-tested, rich ecosystem |
| Auth | djangorestframework-simplejwt | JWT tokens, refresh rotation |
| Real-time | Django Channels (WebSockets) | Push task progress to client |
| Task Queue | Celery 5 | Distributed background tasks |
| Message Broker | Redis 7 | Fast, supports pub/sub |
| Cache | Redis (same instance, different DB) | Query caching, result caching |
| File Storage | django-storages + MinIO (local S3-compatible) | Free local S3, swap to AWS S3 in prod |
| Search | django-watson or PostgreSQL full-text | History search |
| Admin | Django Admin + django-unfold | Enhanced admin UI |

### Backend (AI Services — Optional FastAPI Microservice)

| Layer | Technology | Reason |
|---|---|---|
| Framework | FastAPI | Async-native, fast inference endpoints |
| Model Runtime | Hugging Face Transformers | Access to thousands of SOTA models |
| ONNX Runtime | onnxruntime | Optimized CPU inference |
| OCR | Tesseract 5 + easyocr | Best open-source OCR combo |
| Speech | OpenAI Whisper (offline) | Best open-source STT |
| Embeddings | sentence-transformers | Semantic similarity for plagiarism |

### Database

| Service | Technology | Reason |
|---|---|---|
| Primary DB | PostgreSQL 16 | ACID, JSON support, full-text search |
| Cache/Queue | Redis 7 | Sub-ms reads, pub/sub |
| File Store | MinIO (dev) / AWS S3 (prod) | S3-compatible, scalable |
| Search Index | PostgreSQL pg_trgm extension | Trigram search on history |

---

## 4. Recommended AI Models Per Feature

> All models listed here are open-source and can run on CPU (slowly) or GPU (fast). Each has a HuggingFace or GitHub download link.

### 4.1 Summarizer

**Primary Model**: `facebook/bart-large-cnn`
- Task: Abstractive summarization
- Size: ~1.6 GB
- Speed: ~5–15 seconds per document (CPU), <2s (GPU)
- Library: `transformers` pipeline (`summarization`)
- Usage: Short, detailed, and bullet-point summaries

**For Very Long Documents (>1000 words)**:
`allenai/led-large-16384` (Longformer Encoder-Decoder)
- Handles up to 16,384 tokens
- Ideal for research papers and long articles

**Lightweight Alternative** (for CPU-only deployments):
`sshleifer/distilbart-cnn-12-6` — 50% smaller, 90% of quality

**Implementation Note**: For bullet-point summaries, post-process the BART output by prompting it to return a numbered list, or use a T5 model with a specific prompt: `"summarize as bullet points: {text}"`.

### 4.2 Translator

**Primary Model**: `Helsinki-NLP/opus-mt-{src}-{tgt}`
- Collection of 1000+ language-pair models (e.g., `opus-mt-en-fr`, `opus-mt-en-es`)
- Each model: ~300 MB
- Speed: Fast on CPU for short texts
- Supports 140+ languages

**Multilingual Alternative**: `facebook/nllb-200-distilled-600M`
- Single model for 200 languages
- Size: ~2.4 GB
- Better quality but slower; great for production

**For Contextual Translation** (academic tone): Fine-tuned Helsinki or NLLB models

**Strategy**: Cache the last 3 translation models in memory. Use lazy loading — don't load a language pair until it's requested.

### 4.3 Paraphraser

**Primary Model**: `humarin/chatgpt_paraphraser_on_T5_base`
- Task: Paraphrasing with style control
- Size: ~900 MB
- Styles: formal, casual, fluent, creative

**Alternative**: `Vamsi/T5_Paraphrase_Paws`
- More academic-friendly outputs

**Multiple Styles Strategy**:
- Fluent: Default T5 paraphrase
- Formal: Prepend prompt `"paraphrase formally: "`
- Creative: Higher temperature (1.2), top_p 0.95
- Simple: Add `"simplify and paraphrase: "` prefix

### 4.4 Humanizer

**Strategy**: There is no single "humanizer" model because humanization is a style transformation task. Use a combination approach:

1. **Primary**: `google/flan-t5-large` with a crafted prompt:
   `"Rewrite the following to sound more natural and human: {text}"`
2. **Secondary pass**: Paraphrase with `humarin/chatgpt_paraphraser_on_T5_base`
3. **Post-processing**: Vary sentence lengths, replace overly formal words, add transition words.
4. **Perplexity check**: Use a language model perplexity scorer to verify the output "feels" more human (higher perplexity = more natural variance).

**Important**: No open-source model is perfect at humanization. Combine model output with rule-based post-processing (see Section 18 for full details).

### 4.5 Plagiarism Checker

**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- Size: ~80 MB (very small!)
- Speed: Extremely fast — encodes 500 sentences/second on CPU
- Purpose: Generate semantic embeddings for sentence comparison

**Process**:
1. Split both documents into sentences
2. Encode all sentences using the embedding model
3. Compute cosine similarity matrix between all sentence pairs
4. Flag pairs with similarity > 0.85 as potential plagiarism
5. Group flagged sentences into "plagiarism blocks"

**External Source Comparison**: Use DuckDuckGo or SerpAPI free tier to search suspicious phrases and compare against web content (optional, requires internet).

### 4.6 Image to Text (OCR)

**Primary**: `tesseract 5.x` via `pytesseract`
- Languages: 100+ language packs
- Best for: Clean printed text, PDFs

**Secondary/Handwriting**: `easyocr`
- Better for noisy images, handwriting, curved text
- Size: ~200 MB per language model

**Deep Learning OCR** (optional GPU): `microsoft/trocr-large-printed`
- Transformer-based, highest accuracy for printed text
- Size: ~1.3 GB

**Strategy**: Use Tesseract first (fast). If confidence score < 70%, fall back to EasyOCR. For handwritten documents, always use EasyOCR or TrOCR.

### 4.7 Voice to Text

**Primary Model**: OpenAI Whisper (`openai-whisper` Python package)
- Models: tiny (39M), base (74M), small (244M), medium (769M), large (1.5B)
- **Recommended default**: `whisper-small` for CPU, `whisper-medium` for GPU
- Languages: 99 languages with automatic detection
- Speed: ~5–10x real-time on CPU for `small` model
- License: MIT — completely free, fully offline

**Installation**: `pip install openai-whisper`
**GPU Acceleration**: Automatic if CUDA is available

**Streaming/Chunked Transcription**: For long lectures (>30 min), split audio into 30-second chunks, transcribe in parallel using Celery, then merge transcripts.

### 4.8 YouTube Video Summarizer

**Download**: `yt-dlp` (Python) — free, maintained, downloads YouTube audio/subtitles
**Transcript Extraction**: YouTube auto-captions via `youtube-transcript-api`
**Fallback**: If no captions, download audio → Whisper transcription
**Summarization**: BART or LED (same as summarizer module)

**Libraries**:
```
yt-dlp            # Audio download
youtube-transcript-api   # Caption extraction
openai-whisper    # Fallback transcription
```

---

## 5. Complete Folder Structure

```
scholar-ai/
├── README.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
│
├── backend/                          # Django project root
│   ├── manage.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   │
│   ├── config/                       # Django project settings
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py               # Shared settings
│   │   │   ├── development.py        # Dev overrides
│   │   │   └── production.py         # Prod overrides
│   │   ├── urls.py                   # Root URL config
│   │   ├── asgi.py                   # ASGI for WebSockets
│   │   └── celery.py                 # Celery app config
│   │
│   ├── apps/
│   │   ├── accounts/                 # User auth & profiles
│   │   │   ├── models.py             # CustomUser model
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── tests.py
│   │   │
│   │   ├── history/                  # AI usage history
│   │   │   ├── models.py             # AIHistory model
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── filters.py            # Search/filter logic
│   │   │   └── urls.py
│   │   │
│   │   ├── files/                    # File upload management
│   │   │   ├── models.py             # UploadedFile model
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── validators.py
│   │   │   └── urls.py
│   │   │
│   │   ├── ai_tasks/                 # Celery task hub
│   │   │   ├── tasks/
│   │   │   │   ├── summarize.py
│   │   │   │   ├── translate.py
│   │   │   │   ├── paraphrase.py
│   │   │   │   ├── humanize.py
│   │   │   │   ├── plagiarism.py
│   │   │   │   ├── ocr.py
│   │   │   │   ├── voice.py
│   │   │   │   └── youtube.py
│   │   │   ├── consumers.py          # WebSocket consumers
│   │   │   ├── routing.py            # WebSocket URL routing
│   │   │   └── utils.py
│   │   │
│   │   ├── summarizer/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── translator/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── paraphraser/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── humanizer/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── plagiarism/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── ocr/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   ├── voice/
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   │
│   │   └── youtube/
│   │       ├── views.py
│   │       └── urls.py
│   │
│   └── ai_engine/                    # Core AI processing library
│       ├── __init__.py
│       ├── model_registry.py         # Central model loader/cache
│       ├── summarizer.py
│       ├── translator.py
│       ├── paraphraser.py
│       ├── humanizer.py
│       ├── plagiarism_detector.py
│       ├── ocr_processor.py
│       ├── speech_processor.py
│       ├── youtube_processor.py
│       └── utils/
│           ├── text_chunker.py       # Split long documents
│           ├── language_detector.py
│           └── file_converter.py
│
├── frontend/                         # Next.js project
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   │
│   ├── public/
│   │   └── assets/
│   │
│   └── src/
│       ├── app/                      # Next.js App Router
│       │   ├── layout.tsx            # Root layout
│       │   ├── page.tsx              # Landing page
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   └── register/page.tsx
│       │   ├── (dashboard)/
│       │   │   ├── layout.tsx        # Dashboard shell
│       │   │   ├── dashboard/page.tsx
│       │   │   ├── summarizer/page.tsx
│       │   │   ├── translator/page.tsx
│       │   │   ├── paraphraser/page.tsx
│       │   │   ├── humanizer/page.tsx
│       │   │   ├── plagiarism/page.tsx
│       │   │   ├── ocr/page.tsx
│       │   │   ├── voice/page.tsx
│       │   │   ├── youtube/page.tsx
│       │   │   └── history/
│       │   │       ├── page.tsx      # History list
│       │   │       └── [id]/page.tsx # History detail
│       │   └── api/                  # Next.js API routes (BFF)
│       │       └── proxy/[...path]/route.ts
│       │
│       ├── components/
│       │   ├── ui/                   # shadcn/ui components
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx
│       │   │   ├── Header.tsx
│       │   │   └── MobileNav.tsx
│       │   ├── features/
│       │   │   ├── summarizer/
│       │   │   ├── translator/
│       │   │   ├── paraphraser/
│       │   │   ├── humanizer/
│       │   │   ├── plagiarism/
│       │   │   ├── ocr/
│       │   │   ├── voice/
│       │   │   └── youtube/
│       │   └── shared/
│       │       ├── TaskProgressBar.tsx
│       │       ├── OutputCard.tsx
│       │       ├── HistoryPanel.tsx
│       │       └── FileDropzone.tsx
│       │
│       ├── hooks/
│       │   ├── useWebSocket.ts
│       │   ├── useTaskStatus.ts
│       │   └── useHistory.ts
│       │
│       ├── lib/
│       │   ├── api.ts                # Axios instance + interceptors
│       │   ├── auth.ts               # JWT token management
│       │   └── utils.ts
│       │
│       └── store/
│           ├── authStore.ts
│           └── uiStore.ts
│
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
│
├── models/                           # Downloaded AI model files (gitignored)
│   ├── bart-large-cnn/
│   ├── whisper-small/
│   ├── nllb-200/
│   └── ...
│
└── scripts/
    ├── download_models.sh            # One-command model downloader
    ├── seed_db.py                    # Seed demo data
    └── healthcheck.py
```

---

## 6. Database Schema Design

### Core Tables

```sql
-- Users (extends Django's AbstractUser)
CREATE TABLE accounts_user (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    username        VARCHAR(150) UNIQUE NOT NULL,
    full_name       VARCHAR(200),
    avatar          VARCHAR(500),          -- S3/MinIO URL
    plan            VARCHAR(20) DEFAULT 'free',  -- free | pro | enterprise
    is_verified     BOOLEAN DEFAULT FALSE,
    daily_requests  INTEGER DEFAULT 0,
    monthly_requests INTEGER DEFAULT 0,
    last_reset_date DATE,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Uploaded Files
CREATE TABLE files_uploadedfile (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES accounts_user(id) ON DELETE CASCADE,
    original_name   VARCHAR(500) NOT NULL,
    stored_name     VARCHAR(500) NOT NULL,
    storage_url     VARCHAR(1000),
    file_type       VARCHAR(50),           -- pdf | image | audio | video
    mime_type       VARCHAR(100),
    size_bytes      BIGINT,
    extracted_text  TEXT,                  -- Pre-extracted text cache
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_files_user ON files_uploadedfile(user_id, created_at DESC);

-- AI Usage History (central table for all features)
CREATE TABLE history_aihistory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES accounts_user(id) ON DELETE CASCADE,
    feature         VARCHAR(50) NOT NULL,  -- summarizer | translator | ocr | ...
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | processing | completed | failed
    
    -- Input data
    input_text      TEXT,
    input_file_id   UUID REFERENCES files_uploadedfile(id) ON DELETE SET NULL,
    input_url       VARCHAR(2000),         -- For YouTube
    input_metadata  JSONB DEFAULT '{}',    -- Extra params (e.g., target language)
    
    -- Output data
    output_text     TEXT,
    output_metadata JSONB DEFAULT '{}',    -- Scores, language detected, etc.
    output_file_url VARCHAR(1000),         -- For downloadable outputs
    
    -- Processing metadata
    task_id         VARCHAR(255),          -- Celery task ID
    processing_time FLOAT,                 -- Seconds
    model_used      VARCHAR(100),
    tokens_processed INTEGER,
    
    -- User interactions
    is_starred      BOOLEAN DEFAULT FALSE,
    user_note       TEXT,
    tags            VARCHAR(500)[] DEFAULT '{}',
    
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast history queries
CREATE INDEX idx_history_user_feature ON history_aihistory(user_id, feature);
CREATE INDEX idx_history_user_date ON history_aihistory(user_id, created_at DESC);
CREATE INDEX idx_history_starred ON history_aihistory(user_id, is_starred) WHERE is_starred = TRUE;

-- Full-text search index on history
CREATE INDEX idx_history_fts ON history_aihistory 
    USING gin(to_tsvector('english', coalesce(input_text, '') || ' ' || coalesce(output_text, '')));

-- Plagiarism Results (separate table due to structured data)
CREATE TABLE plagiarism_result (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    history_id      UUID REFERENCES history_aihistory(id) ON DELETE CASCADE,
    overall_score   FLOAT,                 -- 0.0 to 1.0
    matches         JSONB,                 -- Array of {sentence, match, score, source}
    compared_to     VARCHAR(500),          -- 'document_upload' | 'web_search' | 'database'
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Translation History (extra metadata)
CREATE TABLE translator_result (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    history_id      UUID REFERENCES history_aihistory(id) ON DELETE CASCADE,
    source_language VARCHAR(10),
    target_language VARCHAR(10),
    detected_language VARCHAR(10),
    word_count      INTEGER
);

-- API Tokens for programmatic access
CREATE TABLE accounts_apitoken (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES accounts_user(id) ON DELETE CASCADE,
    name            VARCHAR(100),
    token_hash      VARCHAR(64) UNIQUE NOT NULL,  -- SHA-256 of actual token
    last_used       TIMESTAMP,
    expires_at      TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Key Design Decisions

- **UUID primary keys**: Better for distributed systems, prevents enumeration attacks.
- **JSONB for metadata**: Flexible schema for feature-specific data without endless migration.
- **Soft history**: History is never hard-deleted (unless user explicitly purges). This enables undo/redo.
- **Unified history table**: All 8 features share one `ai_history` table with a `feature` discriminator. This enables cross-feature search and analytics.
- **Full-text search index**: PostgreSQL's built-in FTS using `gin` index for fast history search.

---

## 7. Authentication & Authorization System

### JWT-Based Auth Flow

```
Client                    Django API              Redis
  │                          │                      │
  │── POST /auth/register ──>│                      │
  │<─ {access, refresh} ─────│                      │
  │                          │                      │
  │── POST /auth/login ─────>│                      │
  │<─ {access, refresh} ─────│                      │
  │                          │                      │
  │── GET /api/... ──────────│                      │
  │  Authorization: Bearer   │── Check token ──────>│
  │  <access_token>          │<─ Valid/Invalid ──────│
  │<─ 200 OK ────────────────│                      │
  │                          │                      │
  │── POST /auth/refresh ───>│                      │
  │<─ {new_access} ──────────│                      │
```

### Settings (djangorestframework-simplejwt)

```python
# config/settings/base.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,   # Requires rest_framework_simplejwt.token_blacklist
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Authorization Levels

| Level | Capabilities |
|---|---|
| Anonymous | Landing page only |
| Free User | 20 AI requests/day, 5MB file uploads, 30-day history |
| Pro User | 500 requests/day, 50MB uploads, unlimited history, priority queue |
| Admin | Full access, user management, system stats |

### Rate Limiting per Feature

Use `django-ratelimit` for per-user, per-endpoint throttling:

```python
# In DRF settings
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour',
        'anon': '10/hour',
        'ai_tasks': '20/day',   # Custom throttle class
    }
}
```

---

## 8. API Structure

### REST API Endpoints

```
Authentication
  POST   /api/auth/register/
  POST   /api/auth/login/
  POST   /api/auth/logout/
  POST   /api/auth/token/refresh/
  POST   /api/auth/password/reset/
  GET    /api/auth/me/
  PATCH  /api/auth/me/update/

Files
  POST   /api/files/upload/
  GET    /api/files/
  GET    /api/files/{id}/
  DELETE /api/files/{id}/

AI Features — all follow the same pattern:
  POST   /api/summarizer/run/
  POST   /api/translator/run/
  POST   /api/paraphraser/run/
  POST   /api/humanizer/run/
  POST   /api/plagiarism/run/
  POST   /api/ocr/run/
  POST   /api/voice/run/
  POST   /api/youtube/run/
  
  GET    /api/tasks/{task_id}/status/   # Poll task progress

History
  GET    /api/history/
  GET    /api/history/{id}/
  PATCH  /api/history/{id}/
  DELETE /api/history/{id}/
  POST   /api/history/{id}/rerun/
  POST   /api/history/{id}/export/
  GET    /api/history/search/?q=...
  DELETE /api/history/bulk_delete/

Admin (staff only)
  GET    /api/admin/stats/
  GET    /api/admin/users/
  PATCH  /api/admin/users/{id}/
```

### Request/Response Contract for AI Endpoints

All AI endpoints follow this pattern for consistency:

```json
// REQUEST: POST /api/summarizer/run/
{
  "input_type": "text",           // "text" | "file" | "url"
  "text": "The article content...",
  "file_id": null,
  "options": {
    "summary_type": "detailed",   // feature-specific options
    "max_length": 300
  }
}

// RESPONSE (immediate — task was queued)
{
  "task_id": "abc-123-def",
  "history_id": "uuid-here",
  "status": "pending",
  "estimated_seconds": 8
}

// POLL: GET /api/tasks/abc-123-def/status/
{
  "task_id": "abc-123-def",
  "status": "completed",         // pending | processing | completed | failed
  "progress": 100,
  "result": {
    "output_text": "Summary here...",
    "metadata": { "word_count": 120 }
  }
}
```

### WebSocket Events (Django Channels)

```
// Client connects to: ws://api/ws/tasks/{user_id}/

// Server pushes:
{
  "type": "task.update",
  "task_id": "abc-123",
  "status": "processing",
  "progress": 45,
  "message": "Processing document..."
}

{
  "type": "task.complete",
  "task_id": "abc-123",
  "history_id": "uuid",
  "result": { ... }
}
```

---

## 9. Backend Workflow

### Request Lifecycle (End-to-End)

```
1. Client sends POST /api/summarizer/run/ with text + options
2. Django view authenticates JWT → extracts user
3. Rate limit check → reject if exceeded
4. Input validation (Zod equivalent: DRF serializer)
5. Create AIHistory record with status='pending'
6. Enqueue Celery task: summarize.delay(history_id, text, options)
7. Return {task_id, history_id, status:'pending'} immediately (< 50ms)

— Background (Celery Worker) —
8. Worker picks up task from Redis queue
9. Update history status → 'processing'
10. Send WebSocket event: {status: 'processing', progress: 10}
11. Load BART model from model_registry cache
12. Pre-process text (clean, chunk if long)
13. Run inference
14. Post-process output
15. Save output to AIHistory.output_text
16. Update status → 'completed'
17. Send WebSocket event: {status: 'completed', result: {...}}

— Client receives WebSocket event —
18. React Query invalidates history cache
19. UI updates with result (no polling needed)
```

### Feature-Specific View Pattern

```python
# apps/summarizer/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.history.models import AIHistory
from apps.ai_tasks.tasks.summarize import run_summarize

class SummarizeView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AITaskThrottle]
    
    def post(self, request):
        serializer = SummarizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create pending history record
        history = AIHistory.objects.create(
            user=request.user,
            feature='summarizer',
            status='pending',
            input_text=serializer.validated_data.get('text'),
            input_metadata=serializer.validated_data.get('options', {})
        )
        
        # Queue Celery task
        task = run_summarize.delay(str(history.id))
        
        # Save task ID for status polling
        history.task_id = task.id
        history.save(update_fields=['task_id'])
        
        return Response({
            'task_id': task.id,
            'history_id': str(history.id),
            'status': 'pending'
        }, status=202)
```

---

## 10. AI Processing Pipeline

### Central Model Registry

The `model_registry.py` is the most important architectural piece. It acts as a singleton that loads models once and caches them in memory. Loading a model from disk takes 10–30 seconds; loading from RAM cache takes <1ms.

```python
# ai_engine/model_registry.py
import threading
from functools import lru_cache
from transformers import pipeline, AutoTokenizer, AutoModel

class ModelRegistry:
    """Thread-safe, lazy-loading model cache."""
    
    _instance = None
    _lock = threading.Lock()
    _models = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get_model(self, model_name: str, task: str = None):
        """Load model on first access, return cached on subsequent."""
        cache_key = f"{task}:{model_name}" if task else model_name
        
        if cache_key not in self._models:
            with self._lock:
                if cache_key not in self._models:
                    print(f"Loading model: {model_name}")
                    self._models[cache_key] = pipeline(
                        task,
                        model=f"models/{model_name}",
                        device=-1  # -1 = CPU, 0 = first GPU
                    )
                    print(f"Model loaded: {model_name}")
        
        return self._models[cache_key]
    
    def warm_up(self, model_names: list):
        """Pre-load critical models on startup."""
        for name, task in model_names:
            self.get_model(name, task)

# models to warm up on worker start
STARTUP_MODELS = [
    ("facebook/bart-large-cnn", "summarization"),
    ("sentence-transformers/all-MiniLM-L6-v2", None),
]
```

### Text Chunking for Long Documents

Many models have a 512 or 1024 token limit. Long documents must be chunked:

```python
# ai_engine/utils/text_chunker.py
def chunk_text(text: str, max_tokens: int = 900, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    overlap: number of words to repeat at chunk boundaries 
             to preserve context.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + max_tokens]
        chunks.append(' '.join(chunk))
        i += max_tokens - overlap
    return chunks

def merge_summaries(summaries: list[str], model) -> str:
    """Summarize a list of chunk summaries into one final summary."""
    combined = ' '.join(summaries)
    if len(combined.split()) < 900:
        return model(combined)[0]['summary_text']
    # Recursive merge if still too long
    return merge_summaries(
        [model(s)[0]['summary_text'] for s in summaries], 
        model
    )
```

---

## 11. Offline Model Integration Strategy

### Model Download & Management

```bash
# scripts/download_models.sh
# Run once during setup or in Dockerfile build

MODELS_DIR="./models"

# Summarizer
huggingface-cli download facebook/bart-large-cnn --local-dir $MODELS_DIR/bart-large-cnn

# Paraphraser  
huggingface-cli download humarin/chatgpt_paraphraser_on_T5_base --local-dir $MODELS_DIR/t5-paraphrase

# Embeddings (Plagiarism)
huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir $MODELS_DIR/minilm-l6-v2

# Translator (NLLB 200 languages)
huggingface-cli download facebook/nllb-200-distilled-600M --local-dir $MODELS_DIR/nllb-200

# Whisper (Voice-to-Text)
python -c "import whisper; whisper.load_model('small', download_root='./models/whisper')"
```

### Model Storage in Docker

```dockerfile
# In Dockerfile, models are stored as a separate layer
# This allows rebuilding the app without re-downloading models

FROM python:3.11-slim AS base
# ... app setup ...

# Models are mounted as a Docker volume in production
# VOLUME /app/models
```

**Best Practice**: Mount a persistent Docker volume at `/app/models`. On first run, if the model directory is empty, auto-download. On subsequent runs, models are loaded from the mounted volume — no download needed.

### ONNX Optimization (Optional, for CPU speed improvement)

Convert Transformers models to ONNX for 2–4x CPU speedup:

```python
# scripts/convert_to_onnx.py
from optimum.onnxruntime import ORTModelForSeq2SeqLM

model = ORTModelForSeq2SeqLM.from_pretrained(
    "facebook/bart-large-cnn",
    export=True
)
model.save_pretrained("models/bart-large-cnn-onnx")
```

---

## 12. User History Management Architecture

### History Data Flow

```
AI Task Completes
       │
       ▼
AIHistory record updated (status=completed, output_text=...)
       │
       ├──► WebSocket push to user's browser
       │
       └──► Background: Generate history thumbnail/preview
            (first 100 chars of output, word count, etc.)

User Opens History Page
       │
       ▼
GET /api/history/?page=1&feature=summarizer&q=machine+learning
       │
       ▼
PostgreSQL query with:
- Full-text search on input + output text
- Filter by feature, date range, starred
- Paginated (20 per page)
- Sorted by created_at DESC
       │
       ▼
Return paginated history list with previews
```

### History Features

**Search**: Full-text search across input and output text using PostgreSQL `tsvector`.

**Filters**:
- Feature type (summarizer, OCR, translator, etc.)
- Date range (today, this week, this month, custom)
- Status (completed, failed)
- Starred items

**Bulk Actions**:
- Select all / select range
- Bulk delete
- Bulk export (ZIP of .txt files)
- Bulk tag

**Re-run**: `POST /api/history/{id}/rerun/` — creates a new task with the same input. Previous result is preserved in history.

**Export Formats**:
- Copy to clipboard (plain text)
- Download as .txt
- Download as .docx (using python-docx)
- Download as .pdf (using reportlab or weasyprint)

---

## 13. File Upload System

### Upload Flow

```
Client (browser)
  │
  │── 1. POST /api/files/upload/ (multipart/form-data)
  │         max size: 50MB (pro), 5MB (free)
  │
  ▼
Django View
  │── 2. Validate: file type whitelist, virus scan (optional)
  │── 3. Generate UUID filename (prevent path traversal)
  │── 4. Upload to MinIO (dev) or S3 (prod) via django-storages
  │── 5. Create UploadedFile DB record
  │── 6. Return {file_id, name, size, url}
  │
  ▼
Background (Celery)
  └── 7. Extract text preview (for PDFs: pdfplumber, for images: quick OCR)
      └── 8. Update UploadedFile.extracted_text
```

### Supported File Types

| Category | Extensions | Processing |
|---|---|---|
| Documents | .pdf, .docx, .txt, .md | pdfplumber / python-docx / plain read |
| Images | .jpg, .jpeg, .png, .webp, .tiff | PIL + OCR pre-extraction |
| Audio | .mp3, .wav, .m4a, .ogg | Whisper transcription |
| Video | .mp4 (limited) | FFmpeg audio extraction → Whisper |

### Security Validations

```python
ALLOWED_MIME_TYPES = {
    'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain', 'image/jpeg', 'image/png', 'image/webp',
    'audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg',
}

def validate_upload(file):
    # 1. Check MIME type by magic bytes (not extension)
    import magic
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError("File type not allowed")
    
    # 2. Check file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError("File too large")
    
    # 3. Sanitize filename
    safe_name = secure_filename(file.name)
    return safe_name
```

---

## 14. Async / Background Task Processing

### Celery Configuration

```python
# config/celery.py
from celery import Celery

app = Celery('scholar_ai')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Task routing — send AI tasks to dedicated 'ai' queue
app.conf.task_routes = {
    'apps.ai_tasks.tasks.*': {'queue': 'ai'},
    'apps.files.*': {'queue': 'files'},
}

# Priority: voice > youtube > ocr > text tasks
app.conf.task_default_priority = 5
```

### Queue Architecture

```
Redis (Message Broker)
├── Queue: "default"     → Quick tasks (auth, history queries)
├── Queue: "ai"          → AI inference tasks (Celery workers)
├── Queue: "files"       → File upload/processing
└── Queue: "priority"    → Pro user fast lane
```

### Task Progress Reporting

```python
# apps/ai_tasks/tasks/summarize.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task(bind=True, max_retries=3)
def run_summarize(self, history_id: str):
    channel_layer = get_channel_layer()
    history = AIHistory.objects.get(id=history_id)
    user_id = str(history.user_id)
    
    def send_progress(progress: int, message: str):
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {"type": "task.update", "task_id": self.request.id, 
             "progress": progress, "message": message}
        )
    
    try:
        history.status = 'processing'
        history.save()
        send_progress(10, "Loading model...")
        
        registry = ModelRegistry.get_instance()
        model = registry.get_model("facebook/bart-large-cnn", "summarization")
        send_progress(30, "Processing document...")
        
        text = history.input_text
        options = history.input_metadata
        
        # Chunk if needed
        if len(text.split()) > 900:
            chunks = chunk_text(text)
            summaries = []
            for i, chunk in enumerate(chunks):
                result = model(chunk, max_length=150, min_length=40)[0]['summary_text']
                summaries.append(result)
                send_progress(30 + (i / len(chunks)) * 60, f"Processing chunk {i+1}/{len(chunks)}")
            output = merge_summaries(summaries, model)
        else:
            output = model(text, max_length=options.get('max_length', 200))[0]['summary_text']
        
        send_progress(95, "Saving result...")
        history.output_text = output
        history.status = 'completed'
        history.processing_time = time.time() - start_time
        history.save()
        
        # Final WebSocket push
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {"type": "task.complete", "task_id": self.request.id,
             "history_id": history_id, "result": {"output_text": output}}
        )
        
    except Exception as exc:
        history.status = 'failed'
        history.save()
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

---

## 15. OCR Pipeline Architecture

### Multi-Strategy OCR

```
Input Image/PDF
      │
      ▼
Pre-processing (Pillow)
  - Convert to grayscale
  - Adjust contrast/brightness
  - Deskew (correct rotation)
  - Denoise
      │
      ▼
Strategy Selection
  ├── Printed/clean text → Tesseract 5 (fast, 95%+ accuracy)
  ├── Noisy/degraded → EasyOCR (slower, handles noise well)
  └── Handwriting → TrOCR (slowest, best accuracy)
      │
      ▼
Post-processing
  - Remove OCR artifacts (random chars)
  - Fix common OCR errors (l→1, O→0 in numbers)
  - Language detection
  - Format preservation (paragraphs, columns)
      │
      ▼
Return editable text + confidence score
```

### PDF OCR

```python
# ai_engine/ocr_processor.py
import pdfplumber
import pytesseract
from PIL import Image
import easyocr

class OCRProcessor:
    def process_pdf(self, file_path: str) -> dict:
        result_pages = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Try text extraction first (for digital PDFs)
                text = page.extract_text()
                
                if text and len(text.strip()) > 50:
                    # Digital PDF — no OCR needed
                    result_pages.append({
                        'page': page_num + 1,
                        'text': text,
                        'method': 'digital'
                    })
                else:
                    # Scanned PDF — render page as image then OCR
                    img = page.to_image(resolution=300).original
                    text = self.ocr_image(img)
                    result_pages.append({
                        'page': page_num + 1,
                        'text': text,
                        'method': 'ocr'
                    })
        
        return {
            'pages': result_pages,
            'full_text': '\n\n'.join(p['text'] for p in result_pages)
        }
    
    def ocr_image(self, image: Image.Image, strategy='auto') -> str:
        # Pre-process
        image = self._preprocess(image)
        
        # Tesseract first
        tesseract_result = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT
        )
        avg_confidence = sum(
            c for c in tesseract_result['conf'] if c > 0
        ) / max(len([c for c in tesseract_result['conf'] if c > 0]), 1)
        
        if avg_confidence > 70:
            return ' '.join(tesseract_result['text'])
        else:
            # Fall back to EasyOCR
            reader = easyocr.Reader(['en'])
            result = reader.readtext(np.array(image))
            return ' '.join([r[1] for r in result])
```

---

## 16. Voice-to-Text Pipeline

### Whisper Integration

```python
# ai_engine/speech_processor.py
import whisper
import ffmpeg
import os
from pathlib import Path

class SpeechProcessor:
    def __init__(self, model_size='small'):
        self.model = whisper.load_model(
            model_size,
            download_root='models/whisper'
        )
    
    def transcribe(self, audio_path: str, language=None) -> dict:
        """
        Transcribe audio file.
        Returns: {text, language, segments, duration}
        """
        # Convert to WAV if needed (Whisper works best with WAV)
        wav_path = self._convert_to_wav(audio_path)
        
        result = self.model.transcribe(
            wav_path,
            language=language,           # None = auto-detect
            verbose=False,
            word_timestamps=True,        # Enable word-level timing
            task='transcribe'            # 'transcribe' or 'translate' (to English)
        )
        
        # Clean up temp WAV
        if wav_path != audio_path:
            os.remove(wav_path)
        
        return {
            'text': result['text'],
            'language': result['language'],
            'segments': result['segments'],  # [{start, end, text}]
            'duration': result['segments'][-1]['end'] if result['segments'] else 0
        }
    
    def _convert_to_wav(self, input_path: str) -> str:
        """Convert any audio format to 16kHz mono WAV."""
        if input_path.endswith('.wav'):
            return input_path
        
        output_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
        (
            ffmpeg
            .input(input_path)
            .output(output_path, ac=1, ar=16000)  # mono, 16kHz
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
```

### Long Audio Chunking (for 1+ hour lectures)

```python
def transcribe_long_audio(self, audio_path: str, chunk_minutes=5) -> str:
    """Chunk long audio files for parallel processing."""
    duration = get_audio_duration(audio_path)
    chunk_seconds = chunk_minutes * 60
    
    chunks = []
    for start in range(0, int(duration), chunk_seconds):
        end = min(start + chunk_seconds, duration)
        chunk_path = f"/tmp/chunk_{start}_{end}.wav"
        
        ffmpeg.input(audio_path, ss=start, t=end-start).output(chunk_path).run()
        chunks.append((start, chunk_path))
    
    # Transcribe each chunk (parallelizable with Celery group)
    results = []
    for start, chunk_path in chunks:
        result = self.transcribe(chunk_path)
        results.append({'start': start, 'text': result['text']})
    
    return '\n'.join(r['text'] for r in sorted(results, key=lambda x: x['start']))
```

---

## 17. YouTube Processing Workflow

```
User Input: YouTube URL
       │
       ▼
Step 1: Extract Video ID and metadata
  youtube-dl / yt-dlp: video title, description, duration
       │
       ▼
Step 2: Try transcript first (fastest path)
  youtube-transcript-api → fetch auto-generated or manual captions
  ├── Success → go to Step 4
  └── Fail (no captions) → Step 3
       │
       ▼
Step 3: Download audio + transcribe (slow path)
  yt-dlp: download audio-only (m4a/mp3, lowest quality)
  → Whisper transcription (takes 2-10 minutes for 1-hour video)
       │
       ▼
Step 4: Summarize transcript
  → BART or LED summarization
  → Generate: short summary, key points (5-10 bullets), full notes
       │
       ▼
Step 5: Return structured output
  {
    "title": "Video title",
    "url": "...",
    "duration": "1:23:45",
    "summary": "...",
    "key_points": ["...", "..."],
    "full_transcript": "...",
    "timestamps": [{"time": "0:05", "topic": "Intro"}]
  }
```

### Implementation

```python
# ai_engine/youtube_processor.py
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

class YouTubeProcessor:
    def get_transcript(self, video_id: str) -> str:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return ' '.join([t['text'] for t in transcript])
        except Exception:
            return None
    
    def download_audio(self, url: str, output_path: str) -> str:
        ydl_opts = {
            'format': 'worstaudio/worst',  # Low quality, small file
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            return f"{output_path}/{info['id']}.mp3"
    
    def process(self, url: str) -> dict:
        video_id = self._extract_id(url)
        
        # Try captions first
        transcript = self.get_transcript(video_id)
        
        if not transcript:
            # Download + transcribe
            audio_path = self.download_audio(url, '/tmp')
            speech_proc = SpeechProcessor()
            transcript = speech_proc.transcribe(audio_path)['text']
        
        # Summarize
        summarizer = ModelRegistry.get_instance().get_model(
            "facebook/bart-large-cnn", "summarization"
        )
        summary = self._hierarchical_summarize(transcript, summarizer)
        
        return {
            'transcript': transcript,
            'summary': summary,
            'key_points': self._extract_key_points(transcript)
        }
```

---

## 18. Humanizer Implementation Strategy

Humanization is the hardest feature because there's no single "humanizer" model. Use a 3-layer approach:

### Layer 1: Structural Transformation
- Vary sentence length: break up uniform sentences, combine short choppy ones.
- Add transition words: "however", "moreover", "interestingly", "in fact".
- Replace passive voice with active voice (using SpaCy).
- Remove hedging language common in AI outputs ("It is important to note that").

### Layer 2: Vocabulary Diversification
- Replace overused AI words: "delve", "harness", "crucial", "utilize" → natural alternatives.
- Use a thesaurus approach: `nltk.corpus.wordnet` for synonyms.
- Replace all-caps emphasis with italics/restructuring.

### Layer 3: T5 Paraphrase Pass
- Run the structurally modified text through `humarin/chatgpt_paraphraser_on_T5_base` with `creative` style.
- This adds natural variation that's hard to flag as AI.

```python
# ai_engine/humanizer.py
import spacy
from transformers import pipeline

AI_PHRASES = {
    "it is important to note": "notably",
    "in conclusion": "to sum up",
    "utilize": "use",
    "leverage": "use",
    "delve into": "explore",
    "crucially": "",
    "furthermore": "also",
    "in order to": "to",
}

class Humanizer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.paraphraser = pipeline(
            "text2text-generation",
            model="models/t5-paraphrase"
        )
    
    def humanize(self, text: str) -> str:
        # Layer 1: Replace AI phrases
        for phrase, replacement in AI_PHRASES.items():
            text = text.lower().replace(phrase, replacement)
        
        # Layer 2: SpaCy structural changes
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        modified_sentences = []
        for i, sent in enumerate(sentences):
            # Add transition words periodically
            if i > 0 and i % 3 == 0:
                sent = self._add_transition(sent)
            modified_sentences.append(sent)
        
        modified_text = ' '.join(modified_sentences)
        
        # Layer 3: Paraphrase pass
        result = self.paraphraser(
            f"paraphrase: {modified_text}",
            max_length=len(text.split()) + 50,
            temperature=1.1,
            num_return_sequences=1
        )
        
        return result[0]['generated_text']
```

---

## 19. Plagiarism Detection Strategy

### Semantic Similarity Approach (No External API Needed)

```python
# ai_engine/plagiarism_detector.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk

class PlagiarismDetector:
    def __init__(self):
        self.model = SentenceTransformer('models/minilm-l6-v2')
    
    def check(self, text_a: str, text_b: str, threshold=0.85) -> dict:
        """Compare two documents for plagiarism."""
        sentences_a = nltk.sent_tokenize(text_a)
        sentences_b = nltk.sent_tokenize(text_b)
        
        # Encode all sentences
        embeddings_a = self.model.encode(sentences_a)
        embeddings_b = self.model.encode(sentences_b)
        
        # Compute pairwise cosine similarity
        similarity_matrix = cosine_similarity(embeddings_a, embeddings_b)
        
        matches = []
        matched_indices_a = set()
        
        for i, row in enumerate(similarity_matrix):
            max_j = np.argmax(row)
            max_score = row[max_j]
            
            if max_score >= threshold and i not in matched_indices_a:
                matches.append({
                    'original_sentence': sentences_a[i],
                    'matching_sentence': sentences_b[max_j],
                    'similarity_score': float(max_score),
                    'sentence_index_a': i,
                    'sentence_index_b': int(max_j)
                })
                matched_indices_a.add(i)
        
        plagiarism_score = len(matches) / max(len(sentences_a), 1)
        
        return {
            'overall_score': plagiarism_score,
            'percentage': round(plagiarism_score * 100, 1),
            'matches': matches,
            'total_sentences': len(sentences_a),
            'matched_sentences': len(matches)
        }
```

### Single-Document Check (vs. Uploaded History)

For checking a document against the user's own uploaded documents, query the database for all previously uploaded texts, encode them, and compare.

### Web Check (Optional, Internet Required)

Use DuckDuckGo's free search to find suspicious phrases online, then compare extracted web content to the input document. Rate-limit this to 5 checks/day for free users.

---

## 20. Deployment Architecture

### Three Deployment Tiers

**Tier 1 — Local Development**:
```
docker-compose up
→ Django dev server + Celery worker + Redis + PostgreSQL + MinIO
→ All on localhost
```

**Tier 2 — Single Server Production (Budget: $20/month)**:
```
1× VPS (4GB RAM, 2 CPU cores, 80GB SSD)
→ Hetzner CX31 (~$10/month) or DigitalOcean ($24/month)
→ All services in Docker on one machine
→ Nginx for reverse proxy + SSL (Let's Encrypt)
→ CPU-only AI inference
```

**Tier 3 — Scalable Cloud (GPU-accelerated)**:
```
→ AWS EC2 g4dn.xlarge (1× T4 GPU, $0.526/hr, spot pricing)
→ RDS PostgreSQL (managed DB)
→ ElastiCache Redis (managed)
→ S3 for file storage
→ CloudFront CDN
→ ECS or Kubernetes for container orchestration
```

---

## 21. Docker Setup

### docker-compose.yml (Development)

```yaml
version: '3.9'

services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: scholar_ai
      POSTGRES_USER: scholar
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}

  backend:
    build: ./backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
      - ./models:/app/models          # Shared model volume
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file: .env

  celery_worker:
    build: ./backend
    command: celery -A config worker -Q ai,default,files -l info -c 2
    volumes:
      - ./backend:/app
      - ./models:/app/models          # Same model volume
    depends_on:
      - redis
      - db
    env_file: .env
    deploy:
      resources:
        limits:
          memory: 6G                  # Models need RAM

  celery_beat:
    build: ./backend
    command: celery -A config beat -l info
    depends_on:
      - redis
    env_file: .env

  channels:
    build: ./backend
    command: daphne -b 0.0.0.0 -p 8001 config.asgi:application
    ports:
      - "8001:8001"
    depends_on:
      - redis
    env_file: .env

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend/src:/app/src
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_WS_URL: ws://localhost:8001

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  minio_data:
```

### Dockerfile (Backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies for AI libraries
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-eng \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download SpaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000
```

---

## 22. CI/CD Suggestions

### GitHub Actions Pipeline

```yaml
# .github/workflows/deploy.yml
name: Scholar AI CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements-dev.txt
          python manage.py test --settings=config.settings.test
      
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm ci
          npm run type-check
          npm run lint

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and push Docker images
        run: |
          docker build -t scholar-ai-backend ./backend
          docker build -t scholar-ai-frontend ./frontend
          # Push to GitHub Container Registry or DockerHub

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: deploy
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/scholar-ai
            docker-compose pull
            docker-compose up -d --no-deps backend celery_worker frontend
            docker-compose run backend python manage.py migrate
```

---

## 23. GPU / RAM / Storage Requirements

### Minimum (CPU-only, Dev/Small Prod)

| Resource | Requirement | Notes |
|---|---|---|
| RAM | 8 GB | 6 GB for models, 2 GB for OS/app |
| CPU | 4 cores | Inference is slow but works |
| Storage | 40 GB | ~15 GB models + 10 GB app + 15 GB data |
| Network | Any | No external API calls for core features |

### Recommended (CPU Production, ~$20/month hosting)

| Resource | Requirement | Notes |
|---|---|---|
| RAM | 16 GB | Load multiple models simultaneously |
| CPU | 8 cores | Better parallelism |
| Storage | 80 GB SSD | More user files |
| VPS | Hetzner CX41 or equivalent | ~$20/month |

### Optimal (GPU-accelerated)

| Resource | Requirement | Notes |
|---|---|---|
| GPU | NVIDIA T4 (16 GB VRAM) | 10–20x faster inference |
| RAM | 32 GB | Keep all models loaded |
| CPU | 8 cores | For pre/post-processing |
| Storage | 200 GB | More capacity |
| Cost | ~$0.50/hr spot, $300/month reserved | AWS g4dn.xlarge |

### Model Storage Footprint

| Model | Size |
|---|---|
| BART-large-cnn | 1.6 GB |
| Whisper-small | 461 MB |
| NLLB-200-distilled-600M | 2.4 GB |
| T5-paraphrase | 900 MB |
| MiniLM-L6-v2 (plagiarism) | 80 MB |
| EasyOCR (English) | 200 MB |
| SpaCy en_core_web_sm | 12 MB |
| **Total** | **~6 GB** |

---

## 24. Performance Optimization

### Backend Optimizations

**Database Query Optimization**:
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries.
- Add database indexes on frequently queried columns (user_id, feature, created_at).
- Use `defer()` on large text fields when only metadata is needed.
- Pagination: never return all history items; always paginate at 20–50 per page.

**Model Inference**:
- Warm up all models on Celery worker startup — not on first request.
- Use batch inference when processing multiple items simultaneously.
- Enable `torch.compile()` (PyTorch 2.x) for up to 30% CPU speedup.
- Use half-precision (float16) on GPU: `model.half()`.
- Use ONNX Runtime for 2–4x faster CPU inference on supported models.

**Caching**:
- Cache translation results for identical input+language pairs (see Section 25).
- Cache model outputs for frequently-used summarizations (common papers).
- Cache OCR results by file hash — same file never OCR'd twice.

### Frontend Optimizations

- Next.js Image component for automatic WebP conversion and lazy loading.
- Code splitting: each feature page is a separate chunk.
- TanStack Query: cache API responses for 5 minutes, background refetch on focus.
- Virtualize long history lists with `@tanstack/react-virtual`.
- Debounce history search input by 300ms.
- Prefetch next history page on scroll.

---

## 25. Caching Strategy

### Redis Cache Layers

```python
# Layer 1: Model output caching
# Key: SHA256(feature + input_text + options)
# TTL: 7 days (common academic texts reused often)
import hashlib, json
from django.core.cache import cache

def cached_inference(feature, text, options, compute_fn):
    cache_key = hashlib.sha256(
        f"{feature}:{text}:{json.dumps(options, sort_keys=True)}".encode()
    ).hexdigest()
    
    result = cache.get(cache_key)
    if result:
        return result, True  # cache hit
    
    result = compute_fn(text, options)
    cache.set(cache_key, result, timeout=60 * 60 * 24 * 7)  # 7 days
    return result, False  # cache miss

# Layer 2: API response caching (for read endpoints)
# History list: cache for 30 seconds (changes frequently)
# User profile: cache for 5 minutes
# Feature metadata: cache for 1 hour

# Layer 3: Database query caching
# Use django-cacheops for automatic query result caching
CACHEOPS = {
    'history.aihistory': {'ops': 'get', 'timeout': 60},
    'accounts.user': {'ops': 'get', 'timeout': 300},
}

# Layer 4: Session caching
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

---

## 26. Security Best Practices

### Authentication Security
- Rotate refresh tokens on every use (already configured in simplejwt).
- Store access token in memory (JavaScript variable), not localStorage.
- Store refresh token in httpOnly, secure, sameSite=strict cookie.
- Implement account lockout after 5 failed login attempts (django-axes).
- Add email verification for new accounts.

### Input Security
- Validate all file uploads by magic bytes (not file extension).
- Limit upload sizes per user plan.
- Sanitize all text inputs (strip HTML, limit length).
- Use parameterized queries (Django ORM handles this automatically).
- Validate YouTube URLs against a whitelist pattern before downloading.

### API Security
- Rate limiting on all endpoints (especially AI endpoints).
- CORS: only allow your frontend domain.
- Add CSRF protection for non-API endpoints.
- Use HTTPS everywhere (Let's Encrypt is free).
- Never log user content (text, files) to application logs.

### Infrastructure Security
```python
# settings/production.py
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Data Privacy
- Encrypt files at rest (MinIO/S3 server-side encryption).
- Allow users to delete all their data (GDPR right to erasure).
- Auto-delete uploaded files after 30 days (free tier) or 1 year (pro).
- Never send user content to third-party services (offline models prevent this).
- Implement data export: `GET /api/account/export/` returns a ZIP of all user data.

---

## 27. Admin Dashboard Requirements

### Django Admin (django-unfold for better UI)

```python
# Built-in admin capabilities:
# - User management (ban, upgrade plan, reset password)
# - View all AI history (anonymized for privacy)
# - System-wide stats (total requests, popular features, error rate)
# - Queue management (view/cancel pending Celery tasks)
# - Model performance metrics (avg processing time per feature)
# - File storage usage per user

# Custom Admin Views needed:
# 1. System health dashboard (CPU, RAM, queue depth)
# 2. Feature usage analytics (chart by day)
# 3. Error log viewer (failed tasks with error messages)
# 4. Model management (which models are loaded, memory usage)
```

---

## 28. Scalable Enterprise Architecture

### Microservices Evolution Path

```
Phase 1 (Monolith — MVP):
Django monolith + Celery + Redis + PostgreSQL

Phase 2 (AI Microservice):
Django API ←→ FastAPI AI Service (handles model inference)
                    ↑
               Load balanced across 2-3 workers

Phase 3 (Full Microservices):
API Gateway (Kong/Nginx)
    ├── Auth Service (Django)
    ├── History Service (Django)
    ├── File Service (Django)
    └── AI Services (FastAPI × 1 per feature group)
         ├── Text AI Service (summarize, paraphrase, humanize, translate)
         └── Media AI Service (OCR, voice, YouTube)

Phase 4 (Kubernetes):
K8s cluster with:
- Horizontal Pod Autoscaler (scale AI workers based on queue depth)
- GPU node pool for AI inference
- Separate node pools for DB-heavy services
```

---

## 29. Future Upgrade Roadmap

### 6-Month Enhancements
- **Citation Generator**: Input a paper title or DOI → output APA, MLA, Chicago citation.
- **Research Assistant**: Ask questions about uploaded PDFs (RAG with ChromaDB + LangChain).
- **Grammar Checker**: LanguageTool (open-source, self-hosted) for grammar/style checking.
- **Mind Map Generator**: Convert summarized content into visual mind maps (Mermaid.js).

### 12-Month Enhancements
- **Collaborative Documents**: Real-time multi-user document editing (Yjs + WebSockets).
- **AI Tutor Mode**: Q&A on user's uploaded study materials.
- **Export to LaTeX**: Convert academic writing to LaTeX format.
- **Browser Extension**: Chrome extension that adds Scholar AI tools to any webpage.

### 18-Month+ Enhancements
- **Fine-Tuned Models**: Fine-tune summarizer/paraphraser on academic paper datasets.
- **Mobile App**: React Native app sharing the Next.js component library.
- **API Marketplace**: Let developers access Scholar AI via paid API.
- **LMS Integration**: Moodle/Canvas plugins.

---

## 30. MVP Roadmap & Development Phases

### Phase 0 — Project Setup (Week 1–2)
Set up the project skeleton, Docker environment, CI/CD, and baseline auth.

**Deliverables**:
- Docker-compose running PostgreSQL, Redis, Django, Next.js
- User registration, login, JWT auth working
- Basic dashboard layout (no features yet)
- History table created in DB
- File upload endpoint working

### Phase 1 — Core Text Features (Week 3–6)
Build the 3 most requested features first. These share the same text-in/text-out pattern.

**Deliverables**:
- Summarizer (short, detailed, bullets)
- Paraphraser (3 styles)
- Translator (5 most common language pairs)
- Celery worker + WebSocket progress updates
- History system (save, view, copy, delete)

### Phase 2 — Media Features (Week 7–10)
Add features that require file processing.

**Deliverables**:
- Image to Text (OCR) with file upload
- Voice to Text (audio upload + recording)
- YouTube Video Summarizer

### Phase 3 — Advanced Features (Week 11–14)
Add the differentiating features.

**Deliverables**:
- Humanizer
- Plagiarism Checker (document vs. document)
- Advanced history: search, re-run, export, tags, starred

### Phase 4 — Polish & Production (Week 15–16)
**Deliverables**:
- Mobile-responsive UI review
- Performance optimization + caching
- Rate limiting + security hardening
- Admin dashboard
- Production deployment
- Documentation

---

## 31. Production Hosting Recommendations

### Budget Option (~$20/month total)

| Service | Provider | Cost |
|---|---|---|
| VPS (4 vCPU, 8 GB RAM, 80 GB SSD) | Hetzner CX31 | $12/month |
| Domain | Namecheap | $10/year |
| SSL | Let's Encrypt | Free |
| Email (transactional) | Brevo (formerly Sendinblue) | Free tier (300/day) |
| CDN | Cloudflare (free tier) | Free |
| Monitoring | UptimeRobot | Free |
| **Total** | | **~$13/month** |

### Professional Option (~$100/month)

| Service | Provider | Cost |
|---|---|---|
| App Server (8 vCPU, 16 GB RAM) | Hetzner CCX13 | $35/month |
| Managed DB | Hetzner Managed PostgreSQL | $25/month |
| Object Storage | Backblaze B2 (S3-compatible) | ~$5/month |
| Email | Postmark | $15/month |
| Monitoring | Better Uptime + Sentry | $20/month |
| **Total** | | **~$100/month** |

---

## 32. Open-Source AI Models Reference

| Feature | Model | HuggingFace ID | Size | License |
|---|---|---|---|---|
| Summarizer | BART-large-CNN | facebook/bart-large-cnn | 1.6 GB | MIT |
| Summarizer (long) | LED-large-16384 | allenai/led-large-16384 | 1.6 GB | Apache 2.0 |
| Translator | NLLB-200 | facebook/nllb-200-distilled-600M | 2.4 GB | CC-BY-NC-4.0 |
| Paraphraser | T5-paraphrase | humarin/chatgpt_paraphraser_on_T5_base | 900 MB | Apache 2.0 |
| Humanizer | FLAN-T5-large | google/flan-t5-large | 780 MB | Apache 2.0 |
| Plagiarism (embeddings) | MiniLM-L6-v2 | sentence-transformers/all-MiniLM-L6-v2 | 80 MB | Apache 2.0 |
| OCR (primary) | Tesseract 5 | System package | ~50 MB | Apache 2.0 |
| OCR (handwriting) | TrOCR-large | microsoft/trocr-large-printed | 1.3 GB | MIT |
| OCR (noisy) | EasyOCR | pip install easyocr | 200 MB/lang | Apache 2.0 |
| Voice to Text | Whisper-small | openai/whisper-small | 461 MB | MIT |
| Language Detect | LangDetect | pip install langdetect | <1 MB | Apache 2.0 |

---

## 33. Database Optimization Methods

**Indexing**:
- Create composite indexes for common query patterns: `(user_id, feature, created_at)`.
- Use partial indexes for common filters: `WHERE is_starred = TRUE`.
- Use GIN index for full-text search and JSONB queries.

**Connection Pooling**:
- Use PgBouncer or `django-db-connection-pool` to limit DB connections from many Celery workers.
- Set pool size to `(num_workers × 2) + 5`.

**Query Optimization**:
```python
# BAD: N+1 query
histories = AIHistory.objects.filter(user=user)
for h in histories:
    print(h.input_file.original_name)  # N extra queries

# GOOD: Single query with JOIN
histories = AIHistory.objects.filter(user=user).select_related('input_file')
```

**Archiving**:
- After 6 months, move history records to an `archived_history` table.
- Keep only `summary` in the active table; full text is in archive.
- This keeps the active table small and fast.

**Vacuuming**:
- Configure PostgreSQL autovacuum aggressively for the `history` table (high write volume).
- Run `ANALYZE` after bulk imports.

---

## 34. Module Interaction Map

```
User Request
    │
    ▼
Frontend (Next.js)
    │── Auth Token ──────────────────────────────────────────┐
    │── File Upload ─────────────────────────────────────┐   │
    │── AI Request ──────────────────────────────────┐   │   │
    │                                                │   │   │
    ▼                                                ▼   ▼   ▼
Django REST API
    │── accounts app ◄──────────────────────────────────────┘
    │── files app ◄────────────────────────────────────────┘
    │── summarizer/translator/.../views.py ◄───────────────┘
    │
    │── Creates AIHistory record
    │── Enqueues Celery task
    │
    ▼
Celery Worker
    │── Reads AIHistory record
    │── Loads model from ModelRegistry
    │
    │── ai_engine/model_registry.py (shared model cache)
    │       ├── summarizer.py
    │       ├── translator.py
    │       ├── paraphraser.py
    │       ├── humanizer.py
    │       ├── plagiarism_detector.py
    │       ├── ocr_processor.py
    │       ├── speech_processor.py
    │       └── youtube_processor.py
    │
    │── Updates AIHistory.output_text, status='completed'
    │── Pushes WebSocket event via Django Channels + Redis
    │
    ▼
Frontend receives WebSocket event
    │── Invalidates TanStack Query cache
    │── UI updates with result
    │── history app records appear in history list
```

---

## 35. Speed & Accuracy Improvement Tips

### Speed Improvements

1. **Quantize models**: Use `bitsandbytes` to load models in INT8 (half the RAM, 1.5x slower but fits in less memory).
2. **Batch requests**: If multiple users request summarization simultaneously, batch them and run a single model forward pass.
3. **Increase Celery concurrency**: Each worker can handle 2–4 concurrent tasks (use `--concurrency 4`).
4. **Pre-extract text**: When a file is uploaded, immediately extract its text in the background. By the time the user clicks "Summarize", the text is already ready.
5. **Use smaller models by default**: Let users opt into "High Quality" mode (larger model, slower). Default to the distilled/smaller model.
6. **Streaming responses**: For long summarizations, stream the output token by token via WebSocket for a responsive feel (HuggingFace `TextIteratorStreamer`).

### Accuracy Improvements

1. **Prompt engineering**: All T5/FLAN models respond better to explicit prompts. Test multiple prompt formats and pick the highest-scoring one.
2. **Post-processing validation**: After summarization, check that the summary doesn't contain hallucinated entities (compare named entities in input vs. output using SpaCy).
3. **Language detection before translation**: Always auto-detect the source language — let users confirm, not just assume.
4. **OCR confidence scoring**: Never return low-confidence OCR output without flagging it. Show users a confidence percentage and let them retry with a different strategy.
5. **Chunking overlap**: Use 10% overlap between chunks to preserve context at boundaries.
6. **Ensemble for plagiarism**: Use both lexical (TF-IDF) and semantic (embedding) similarity. A sentence can be paraphrased (low lexical, high semantic) or contain exact copied phrases (high lexical, low semantic).

---

## 36. Cursor AI Prompt Guide

Use these prompt templates to implement Scholar AI with Cursor AI efficiently.

### Prompt 1: Project Setup

```
Create a new Django 5 project with the following setup:
- Project name: scholar_ai
- Apps: accounts, history, files, summarizer, translator, paraphraser, humanizer, plagiarism, ocr, voice, youtube, ai_tasks
- Settings split into base.py, development.py, production.py
- Install: djangorestframework, djangorestframework-simplejwt, django-cors-headers, celery, redis, django-storages, channels, daphne
- Configure PostgreSQL database
- Configure Redis for cache and Celery broker
- Create a custom User model extending AbstractUser with fields: id (UUID), email, full_name, plan, daily_requests
- Set up JWT authentication with: ACCESS_TOKEN_LIFETIME=30min, REFRESH_TOKEN_LIFETIME=7days, ROTATE_REFRESH_TOKENS=True
```

### Prompt 2: AIHistory Model

```
In the Django 'history' app, create a model called AIHistory with these fields:
- id: UUIDField primary key
- user: ForeignKey to settings.AUTH_USER_MODEL
- feature: CharField with choices (summarizer, translator, paraphraser, humanizer, plagiarism, ocr, voice, youtube)
- status: CharField with choices (pending, processing, completed, failed)
- input_text: TextField (nullable)
- input_file: ForeignKey to files.UploadedFile (nullable)
- input_url: URLField (nullable)
- input_metadata: JSONField (default empty dict)
- output_text: TextField (nullable)
- output_metadata: JSONField (default empty dict)
- task_id: CharField (nullable)
- processing_time: FloatField (nullable)
- is_starred: BooleanField (default False)
- created_at: auto DateTimeField

Also create a ViewSet with pagination (20 per page), search (full-text on input_text + output_text), filter by feature and date range, and a /rerun/ action.
```

### Prompt 3: Summarizer Feature

```
Create a summarizer module in Django with:
1. A Celery task in apps/ai_tasks/tasks/summarize.py that:
   - Accepts a history_id
   - Loads the AIHistory record
   - Loads facebook/bart-large-cnn using a ModelRegistry singleton
   - Handles texts longer than 900 words by chunking with 50-word overlap
   - Merges chunk summaries recursively
   - Supports options: max_length, summary_type (short/detailed/bullets)
   - Updates history status at each step
   - Sends WebSocket progress events at: 10%, 30%, 70%, 95%, 100%
   - Saves output to history.output_text
2. A Django REST view that accepts POST with {input_type, text, options}, creates a history record, queues the task, and returns {task_id, history_id, status}
```

### Prompt 4: Frontend Feature Page Pattern

```
Create a Next.js 14 TypeScript page for the Summarizer feature at app/(dashboard)/summarizer/page.tsx with:
- A TipTap rich text editor for input (or plain textarea)
- File upload via react-dropzone (accepts .pdf, .docx, .txt)
- Options panel: summary type toggle (short/detailed/bullets), max length slider
- Submit button that calls POST /api/summarizer/run/
- Real-time progress bar that connects to WebSocket and shows task progress
- Output display card with: copy button, download as .txt button, view in history button
- The page should be responsive and use shadcn/ui components
- Use TanStack Query for API calls
- Use Zustand for local UI state
```

---

## 37. Summary: Recommended Development Order

### Feature Priority & Difficulty Matrix

| # | Feature | Difficulty | Est. Dev Time | Priority |
|---|---|---|---|---|
| 1 | Auth + User System | ⭐⭐ Medium | 3 days | Critical |
| 2 | File Upload System | ⭐⭐ Medium | 2 days | Critical |
| 3 | History System (CRUD) | ⭐⭐ Medium | 2 days | Critical |
| 4 | Celery + WebSocket Setup | ⭐⭐⭐ Hard | 3 days | Critical |
| 5 | **Summarizer** | ⭐ Easy | 2 days | MVP Core |
| 6 | **Translator** | ⭐ Easy | 2 days | MVP Core |
| 7 | **Paraphraser** | ⭐ Easy | 1 day | MVP Core |
| 8 | **OCR** | ⭐⭐ Medium | 3 days | MVP Core |
| 9 | **Voice to Text** | ⭐⭐ Medium | 3 days | MVP Core |
| 10 | **YouTube Summarizer** | ⭐⭐⭐ Hard | 4 days | MVP Core |
| 11 | **Humanizer** | ⭐⭐⭐ Hard | 3 days | Phase 2 |
| 12 | **Plagiarism Checker** | ⭐⭐⭐ Hard | 4 days | Phase 2 |
| 13 | Advanced History (search, re-run, export) | ⭐⭐ Medium | 3 days | Phase 3 |
| 14 | Admin Dashboard | ⭐⭐ Medium | 2 days | Phase 4 |
| 15 | Docker + Production Deploy | ⭐⭐ Medium | 3 days | Phase 4 |

### Build Order for Fastest MVP

```
Week 1:  Auth + DB + Docker setup
Week 2:  History system + File uploads + Celery/WebSocket
Week 3:  Summarizer + Translator (same code pattern)
Week 4:  Paraphraser + OCR + basic frontend for all 4
Week 5:  Voice-to-Text + YouTube
Week 6:  Humanizer + Plagiarism
Week 7:  History: search, re-run, export, tags
Week 8:  Frontend polish + Mobile responsiveness
Week 9:  Testing + security audit + performance tuning
Week 10: Production deployment + monitoring + admin panel
```

### Hardware Recommendation for Development

- **Minimum Dev Machine**: 16 GB RAM, any modern CPU (2018+), 50 GB free disk.
- **Recommended Dev Machine**: 32 GB RAM, 6+ core CPU, NVMe SSD.
- **For GPU Testing**: Any NVIDIA GPU with 6+ GB VRAM (RTX 3060, GTX 1080 Ti, etc.) — not required but dramatically speeds up testing Whisper and BART.

### The Rule of Three: Build MVP with These 3 First

If you must launch something in 2 weeks, prioritize:
1. **Summarizer** — highest utility, easiest to build, uses the simplest pipeline.
2. **Translator** — second-most requested academic tool, reuses the same task/WebSocket infra.
3. **History System** — makes the app "sticky" and differentiates it from single-use tools.

These three alone, built well with a polished UI, are a complete and valuable product.

---

*Document prepared for Cursor AI implementation of Scholar AI v1.0*
*Architecture designed for offline-first, low-cost, open-source AI deployment*
*All models listed are freely available on HuggingFace or via pip*
