# Resume AI CRM

AI-powered resume tailoring and job application tracker. Paste a job description, paste your master resume — Gemini tailors the CV and logs the application. Track every role through the full pipeline from generated to offer.

**Live demo:** https://resume-ai-crm-1068162498226.us-central1.run.app

---

## Features

- AI resume tailoring via Gemini API (`gemini-2.5-flash`) — structure-preserving, ATS-optimised
- Master resume passed at generation time — no sensitive files stored on the server
- Job application tracking with status management
- Web UI with FastAPI + Jinja2
- RESTful API (`/api/jobs`)
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

### GCP Resources Required

| Resource | Name |
|----------|------|
| Cloud SQL instance | `resume-crm-db` (Postgres 15, db-f1-micro) |
| Database | `resume_crm` |
| Database user | `resume_user` |
| GCS bucket | `resume-crm-gcb` |
| Service account | `resume-crm-sa` (roles: `cloudsql.client`, `storage.objectAdmin`) |

### Build and deploy

```bash
# Build for AMD64 (Cloud Run target architecture)
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/ayush-resume-crm/resume-ai-crm/resume-ai-crm:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/ayush-resume-crm/resume-ai-crm/resume-ai-crm:latest

# Deploy to Cloud Run
gcloud run deploy resume-ai-crm \
  --image=us-central1-docker.pkg.dev/ayush-resume-crm/resume-ai-crm/resume-ai-crm:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --service-account=resume-crm-sa@ayush-resume-crm.iam.gserviceaccount.com \
  --add-cloudsql-instances=ayush-resume-crm:us-central1:resume-crm-db \
  --set-env-vars="DATABASE_URL=true,DB_HOST=/cloudsql/ayush-resume-crm:us-central1:resume-crm-db,DB_NAME=resume_crm,DB_USER=resume_user,DB_PASS=YOUR_PASSWORD_HERE,GCS_BUCKET_NAME=resume-crm-gcb,GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE" \
  --project=ayush-resume-crm
```

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

---

## Job Statuses

`generated` → `applied` → `interview` → `offer` / `rejected`
