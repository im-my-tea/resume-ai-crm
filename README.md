# Resume AI CRM

AI-powered resume tailoring and job tracking system.

---

## Features

- AI resume generation using Gemini API
- Dynamic JD input (paste via VS Code flow)
- Versioned resume storage (CVs/)
- Job tracking with status updates (SQLite DB)
- CLI dashboard

---

## Tech

- Python
- FastAPI (API layer)
- Gemini API
- SQLite (persistent storage)
- File-based storage for resumes + JDs

---

## Architecture


- app.py → CLI controller
- main.py → resume generation flow
- services/ → business logic
- db/ → database layer
- config.py → centralized config

- JDS/ → stored job descriptions
- CVs/ → generated resumes
- data/jobs.db → database



---

## Run

Start the CLI dashboard:

```bash
python app.py
```