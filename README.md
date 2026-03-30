# Resume AI CRM

AI-powered resume tailoring and job application tracker. Paste a job description, paste your master resume — Gemini tailors the CV and logs the application. Track every role through the full pipeline from generated to offer.

**Live demo:** https://resume-ai-crm-1068162498226.us-central1.run.app

---

## Features

- AI resume tailoring via Gemini API (`gemini-2.5-flash`) — structure-preserving, ATS-optimised
- Master resume passed at generation time — no sensitive files stored on the server
- Job application tracking with status management (SQLite)
- Web UI with FastAPI + Jinja2
- RESTful API (`/api/jobs`)
- CLI dashboard (`app.py`) for local use

---

## Tech Stack

- Python 3.12
- FastAPI + Jinja2 (web layer)
- Google Gemini API (`gemini-2.5-flash`)
- SQLite (job tracking)
- Pydantic (request/response validation)
- Docker + GCP Cloud Run (deployment)

---

## Architecture

```
api.py              # FastAPI app — UI routes + REST API
config.py           # Centralised config (model, paths, DB)
services/
  ai_service.py     # Gemini prompt + response handling
  job_service.py    # SQLite CRUD (load, get, add, update)
  resume_service.py # Resume file saving + versioning
db/
  schema.sql        # Jobs table schema
  database.py       # DB connection utility
templates/
  base.html         # Base layout
  index.html        # Job list view
  job_detail.html   # Job detail + status update
  generate.html     # Resume generation form
JDs/                # Stored job descriptions (gitignored)
CVs/                # Generated resume versions (gitignored)
data/jobs.db        # SQLite database (gitignored)
```

### Request flow

```
Browser
  ↓  POST /generate (company, role, jd_text, master_resume)
FastAPI (api.py)
  ↓
ai_service.py  →  Gemini API  →  tailored resume text
  ↓
resume_service.py  →  saves to CVs/
job_service.py     →  writes record to SQLite
  ↓
Redirect → / (job list)
```

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

```bash
# Build for AMD64 (Cloud Run target architecture)
docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/<PROJECT>/resume-ai-crm/resume-ai-crm:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/<PROJECT>/resume-ai-crm/resume-ai-crm:latest

# Deploy to Cloud Run
gcloud run deploy resume-ai-crm \
  --image us-central1-docker.pkg.dev/<PROJECT>/resume-ai-crm/resume-ai-crm:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

---

## Storage — Current Limitation

Cloud Run containers are stateless. Generated resumes (`CVs/`), saved JDs (`JDs/`), and the SQLite database (`data/jobs.db`) are ephemeral — they reset on every cold start.

**This is acceptable for demo purposes.** The live URL demonstrates the full generation and tracking flow.

**Production migration path:**
- SQLite → Cloud SQL (managed Postgres)
- `CVs/` and `JDs/` → GCS bucket (object storage)
- Master resume → GCS or Secret Manager

For persistent personal use, run locally with `uvicorn api:app --reload` — SQLite and file storage work correctly on a local filesystem.

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