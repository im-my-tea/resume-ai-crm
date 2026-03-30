from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List, Literal
import datetime
import re
import os

from services.ai_service import generate_resume
from services.resume_service import save_resume
from services.job_service import load_jobs, get_job, update_job, update_notes, delete_job, add_job
from config import JOBS_DIR

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# -----------------------
# SCHEMAS
# -----------------------
class ResumeRequest(BaseModel):
    company: str
    role: str
    jd_text: str
    master_resume: str


class StatusUpdateRequest(BaseModel):
    status: Literal[
        "generated",
        "applied",
        "interview",
        "rejected",
        "offer"
    ]


class JobResponse(BaseModel):
    id: int
    company: str
    role: str
    jd_path: str
    resume_path: str
    status: str
    date: str
    edited: bool
    notes: Optional[str] = None


# -----------------------
# UI ROUTES
# -----------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    jobs = load_jobs()
    return templates.TemplateResponse(request, "index.html", {"jobs": jobs})


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_detail_page(request: Request, job_id: int):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_text = None
    try:
        with open(job["resume_path"], "r") as f:
            resume_text = f.read()
    except (FileNotFoundError, TypeError):
        pass

    return templates.TemplateResponse(request, "job_detail.html", {"job": job, "job_id": job_id, "resume_text": resume_text})


@app.post("/jobs/{job_id}/update")
def update_job_status_ui(job_id: int, status: str = Form(...)):
    update_job(job_id, status)

    return RedirectResponse(
        url=f"/jobs/{job_id}",
        status_code=303
    )


@app.post("/jobs/{job_id}/notes")
def update_job_notes(job_id: int, notes: str = Form(...)):
    update_notes(job_id, notes)
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


@app.post("/jobs/{job_id}/delete")
def delete_job_ui(job_id: int):
    delete_job(job_id)
    return RedirectResponse(url="/", status_code=303)


@app.get("/generate", response_class=HTMLResponse)
def generate_page(request: Request):
    return templates.TemplateResponse(request, "generate.html", {})


@app.post("/generate")
def generate_resume_ui(
    request: Request,
    company: str = Form(...),
    role: str = Form(...),
    jd_text: str = Form(...),
    master_resume: str = Form(...)
):
    resume_text = generate_resume(master_resume, jd_text)
    resume_path = save_resume(resume_text)
    os.makedirs(JOBS_DIR, exist_ok=True)
    company_slug = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')
    jd_path = f"{JOBS_DIR}/jd_{company_slug}.txt"
    with open(jd_path, "w") as f:
        f.write(jd_text)
    add_job(company, role, jd_path, resume_path)
    return RedirectResponse(url="/", status_code=303)


# -----------------------
# API ROUTES
# -----------------------

@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs_api():
    return load_jobs()


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job_api(job_id: int):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.patch("/api/jobs/{job_id}", response_model=JobResponse)
def update_job_status_api(job_id: int, request: StatusUpdateRequest):
    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_job(job_id, request.status)

    updated_job = get_job(job_id)
    return updated_job


# -----------------------
# GENERATE RESUME
# -----------------------

@app.post("/generate-resume")
def generate_resume_api(request: ResumeRequest):

    # 1. Generate resume
    resume_text = generate_resume(
        request.master_resume,
        request.jd_text
    )

    # 2. Save resume
    resume_path = save_resume(resume_text)

    # 3. Save JD
    os.makedirs(JOBS_DIR, exist_ok=True)

    company_slug = re.sub(r'[^a-z0-9]+', '-', request.company.lower()).strip('-')
    jd_path = f"{JOBS_DIR}/jd_{company_slug}.txt"

    with open(jd_path, "w") as f:
        f.write(request.jd_text)

    # 4. Save to DB (IMPORTANT FIX)
    add_job(
        request.company,
        request.role,
        jd_path,
        resume_path
    )

    return {
        "message": "Resume generated successfully",
        "resume_path": resume_path
    }