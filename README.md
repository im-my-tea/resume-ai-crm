# Resume AI CRM

AI-powered resume tailoring and job application tracker. Paste a job description, paste your master resume — Gemini tailors the CV and logs the application. Track every role through the full pipeline from generated to offer.

**Live demo:** https://resume-ai-crm-1068162498226.us-central1.run.app

---

## Features

- AI resume tailoring via Gemini API (`gemini-2.5-flash`) — structure-preserving, ATS-optimised
- Master resume passed at generation time — no sensitive files stored on the server
- Job application tracking with status management
- Web UI with FastAPI + Jinja2
- RESTful API (`/api/jobs`) with Pydantic input validation (length-bounded fields, fail-fast 422)
- Readiness probe (`/health`) — DB + GCS connectivity checks, returns 200/503
- Structured JSON logging with per-request `request_id` correlation (`X-Request-ID` header + error body)
- Circuit breaker on Gemini calls — trips after 5 consecutive failures, 60s cooldown, half-open probe
- Graceful degradation — 503 with structured body (HTML for UI, JSON for API) when the breaker is open; no partial DB/GCS writes
- Test suite — pytest + FastAPI TestClient, 5 tests, runs on every push via GitHub Actions
- CLI dashboard (`app.py`) for local use
- Dual storage backend — Cloud SQL + GCS in production, SQLite + local filesystem locally

---

## Tech Stack

- Python 3.12
- FastAPI + Jinja2 (web layer)
- Google Gemini API (`gemini-2.5-flash`)
- PostgreSQL via Cloud SQL (production) / SQLite (local)
- GCS (production file storage) / local filesystem (local)
- Pydantic (request/response validation)
- Docker + GCP Cloud Run (deployment)
- GCP Cloud Build (CI/CD — auto-deploys on push to `main`)

---

## Architecture

```
api.py              # FastAPI app — UI routes + REST API
config.py           # Centralised config (model, paths, DB, GCS)
services/
  ai_service.py     # Gemini prompt + response handling
  job_service.py    # DB CRUD (Postgres or SQLite)
  resume_service.py # Resume saving — GCS or local filesystem
db/
  schema.sql        # Jobs table schema (Postgres)
  database.py       # Dual-mode DB connection (Postgres / SQLite)
templates/
  base.html         # Base layout
  index.html        # Job list view
  job_detail.html   # Job detail + status update
  generate.html     # Resume generation form
JDs/                # Stored job descriptions (local only, gitignored)
CVs/                # Generated resume versions (local only, gitignored)
data/jobs.db        # SQLite database (local only, gitignored)
```

### Request flow

```
Browser
  ↓  POST /generate (company, role, jd_text, master_resume)
FastAPI (api.py)
  ↓
ai_service.py  →  Gemini API  →  tailored resume text
  ↓
resume_service.py  →  GCS bucket (cloud) / CVs/ (local)
job_service.py     →  Cloud SQL Postgres (cloud) / SQLite (local)
  ↓
Redirect → / (job list)
```

### Storage mode detection

The app checks for the `DATABASE_URL` environment variable at startup:
- **Set** → cloud mode: Postgres (Cloud SQL) + GCS
- **Not set** → local mode: SQLite + local filesystem

---

## Local Setup

```bash
git clone https://github.com/im-my-tea/resume-ai-crm.git
cd resume-ai-crm
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=your_key_here
```

Initialise the database:

```bash
sqlite3 data/jobs.db < db/schema.sql
```

Run locally:

```bash
uvicorn api:app --reload
```

Open `http://localhost:8000`.

---

## Deployment (GCP Cloud Run)

Deployment is fully automated via **Cloud Build**. Push to `main` → build runs → Cloud Run is updated. No manual steps needed.

```
git push origin main  →  Cloud Build  →  Artifact Registry  →  Cloud Run
```

### GCP Resources

| Resource | Name |
|----------|------|
| Cloud Run service | `resume-ai-crm` — `us-central1` |
| Cloud SQL instance | `resume-crm-db` (Postgres 15) |
| GCS bucket | `ayush-resume-crm-files` |
| Artifact Registry | `resume-ai-crm` — `us-central1` |
| Service account | `resume-crm-sa` (roles: `cloudsql.client`, `storage.objectAdmin`, `Cloud Run Admin`) |
| Cloud Build trigger | `deploy-on-push-main` — fires on push to `^main$` |

### Manual deploy (if needed)

If you ever need to deploy without pushing to `main`, trigger a build manually from **GCP Console → Cloud Build → Triggers → Run**.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Job list UI |
| GET | `/jobs/{id}` | Job detail UI |
| POST | `/jobs/{id}/update` | Update job status (form) |
| GET | `/generate` | Resume generation UI |
| POST | `/generate` | Generate + save tailored resume (form) |
| GET | `/api/jobs` | List all jobs (JSON) |
| GET | `/api/jobs/{id}` | Get job by ID (JSON) |
| PATCH | `/api/jobs/{id}` | Update job status (JSON) |
| POST | `/generate-resume` | Generate resume (JSON API) |
| GET | `/health` | Readiness probe — checks DB and GCS connectivity. 200 if healthy, 503 if degraded |

### Error response shape

Unhandled exceptions are converted by the request-logging middleware into a clean JSON envelope (no stack traces leaked to the caller):

```json
{"error": "internal server error", "request_id": "ea4c84dc-9be5-49ec-90ba-4586ef8c3d67"}
```

The same `request_id` is also stamped on every response as the `X-Request-ID` header, and appears on every log line from that request. Paste the ID when reporting an issue and the full trace can be pulled from Cloud Logging.

---

## Observability

All logs are emitted as single-line JSON (`utils/logger.py`). Each HTTP request is bracketed by a middleware that generates a UUID `request_id`, logs `Request started` / `Request completed` (with `method`, `path`, `status_code`, `duration_ms`), and stamps `X-Request-ID` on the response. Cloud Logging picks up `severity` natively. Service-layer functions (`ai_service`, `job_service`, `resume_service`) log errors with `exc_info=True` and re-raise — exceptions are never swallowed.

---

## Testing

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/
```

The suite covers the happy path on `/generate-resume`, Pydantic 422 validation, `/health` structure, the 503 degraded response when the circuit breaker is open, and that every response carries a UUID4 `X-Request-ID` header. External dependencies (Gemini, DB, GCS, filesystem writes) are mocked with `unittest.mock.patch`. CI runs the same command on every push and PR to `main`.

---

## Job Statuses

`generated` → `applied` → `interview` → `offer` / `rejected`
