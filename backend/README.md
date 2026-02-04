# Murph Backend (FastAPI + Supabase)

This folder contains the **backend only** for the hackathon prototype.

## Prereqs

- Python **3.12.11**
- [`uv`](https://docs.astral.sh/uv/) installed

## Setup

Copy env file and fill in keys:

- Create `backend/.env` from `backend/.env.example`

Install deps:

```bash
cd backend
uv sync
```

## Run

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

API docs:

- Swagger: `http://localhost:8000/docs`

Frontend integration notes:

- CORS is enabled for `http://localhost:5173` (Vite).
- All endpoints return JSON, and errors use HTTP status codes + a consistent JSON shape.

## Supabase setup (one-time)

This backend uses **Supabase Postgres** tables:

- `users`
- `listings`
- `sessions`
- `reviews`
- `payments`

For the hackathon MVP, seeding runs on startup (idempotent via upserts).

Storage:

- Create a bucket named `videos` (or set `SUPABASE_VIDEOS_BUCKET`).
- For easiest dev, set bucket to **public** so the returned `publicUrl` can be played directly.

