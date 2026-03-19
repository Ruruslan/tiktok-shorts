# TikTok Shorts Studio

Production-oriented web application that turns long YouTube videos into **exactly 10 short vertical clips** for TikTok / Reels using FastAPI, Celery, FFmpeg, Whisper-style transcription, and OpenAI-powered semantic segmentation.

## Features

- Submit a validated HTTPS YouTube URL.
- Background pipeline for metadata validation, download, transcription, semantic clip planning, rendering, and subtitle burn-in.
- Generates **10 clips** constrained to **15–60 seconds** with transcript-aware boundaries.
- Regenerate any individual clip with a new semantic segment.
- Modern React/Vite UI with progress tracking, video preview, and download links.
- Docker support for API, worker, frontend, and Redis.
- Security controls for rate limiting, CSRF header checks, strict host allowlists, temporary-file isolation, and log redaction.

## Architecture

### Backend (`backend/`)

- `app/api/v1/jobs.py`: REST API for creating jobs, polling status, and regenerating clips.
- `app/services/youtube.py`: YouTube URL validation, metadata probing, and download handling.
- `app/services/transcription.py`: OpenAI transcription integration.
- `app/services/segmentation.py`: transcript cleanup plus LLM-driven clip selection with deterministic fallback.
- `app/services/video.py`: FFmpeg clipping, 9:16 conversion, face-aware horizontal crop heuristic, and subtitle burn-in.
- `app/workers/tasks.py`: Celery tasks for asynchronous processing.

### Frontend (`frontend/`)

- React + Vite single-page app.
- Progressive status UI with polling.
- Clip grid with HTML5 previews and per-clip regeneration.

## Security notes

- API keys are read from environment variables only.
- Only HTTPS YouTube hosts on an allowlist are accepted.
- Requests are rate-limited and require `X-CSRF-Token` on mutating endpoints.
- Temporary and public media files are written into application-owned directories using job UUIDs.
- Error logs are filtered to avoid leaking known sensitive keys.
- Deployers should only process videos they are authorized to repurpose and must ensure platform-policy compliance in their environment.

## Local development

### 1. Configure environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit the copied files with your real OpenAI key and CSRF token.

### 2. Start dependencies

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Redis: `localhost:6379`

### 3. Run without Docker

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
celery -A app.workers.celery_app.celery_app worker -l info
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API

### `POST /api/v1/jobs`
Create a new processing job.

```json
{ "youtube_url": "https://www.youtube.com/watch?v=..." }
```

### `GET /api/v1/jobs/{job_id}`
Poll job status and retrieve generated clip metadata.

### `POST /api/v1/jobs/{job_id}/regenerate`
Regenerate a specific clip.

```json
{ "clip_id": "existing-clip-id" }
```

## Testing

Backend unit tests:

```bash
cd backend && pytest
```

Frontend build:

```bash
cd frontend && npm install && npm run build
```

## Limitations to be aware of

- OpenAI credentials are required for the production AI path; a deterministic fallback planner exists for local testing.
- Download compatibility depends on the source video, available codecs, and the deployer's legal right to transform the media.
- Face-centric cropping uses a lightweight Haar cascade heuristic; for highest quality you can replace it with a more advanced subject-tracking model.
