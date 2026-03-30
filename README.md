# Resume AI CRM

AI-powered resume tailoring and job application tracker. Uses Google Gemini to tailor a master resume against a job description, then stores the result with full job tracking through a CLI dashboard and web UI.

---

## Features

- AI resume tailoring via Gemini API (structure-preserving, ATS-optimised)
- Dynamic JD input via VS Code editor flow
- Versioned resume storage (`CVs/`)
- Job application tracking with status management (SQLite)
- CLI dashboard (`app.py`)
- Web UI with FastAPI + Jinja2 (`/` and `/jobs/{id}`)
- RESTful API (`/api/jobs`)

---

## Tech Stack

- Python 3.12
- FastAPI + Jinja2 (web layer)
- Google Gemini API (`gemini-2.5-flash`)
- SQLite (persistent job tracking)
- Pydantic (request/response validation)

---

## Architecture

```
app.py              # CLI dashboard (entry point)
main.py             # Resume generation workflow (VS Code + Gemini flow)
api.py              # FastAPI app — UI routes + REST API
config.py           # Centralized config (model, paths, DB)
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
JDs/                # Stored job descriptions (gitignored)
CVs/                # Generated resume versions (gitignored)
data/jobs.db        # SQLite database (gitignored)
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
GOOGLE_API_KEY=your_key_here
```

Initialise the database:

```bash
sqlite3 data/jobs.db < db/schema.sql
```

Add your base resume as `master-resume.txt` in the project root.

---

## Usage

### CLI dashboard

```bash
python app.py
```

Options: generate resume, view jobs, update status, view job details, open resume in VS Code.

### Web UI

```bash
uvicorn api:app --reload
```

Then open `http://localhost:8000`.

### API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{id}` | Get job by ID |
| PATCH | `/api/jobs/{id}` | Update job status |
| POST | `/generate-resume` | Generate + save tailored resume |

---

## Job Statuses

`generated` → `applied` → `interview` → `offer` / `rejected`
