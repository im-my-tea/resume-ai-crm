from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Literal
import datetime
import re
import os

from services.ai_service import generate_resume
from services.resume_service import save_resume
from services.job_service import add_job, load_jobs, update_job
from config import JOBS_DIR

app = FastAPI()

# -----------------------
# REQUEST/RESPONSE SCHEMA
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
# ROOT
# -----------------------
@app.get("/")
def root():
    return {"message": "Resume AI CRM API running"}


# -----------------------
# GET ALL JOBS
# -----------------------
@app.get("/jobs", response_model=List[JobResponse])
def get_jobs():
    return load_jobs()


# -----------------------
# GET SINGLE JOB
# -----------------------
@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int):
    jobs = load_jobs()

    for job in jobs:
        if job["id"] == job_id:
            return job

    raise HTTPException(status_code=404, detail="Job not found")


# -----------------------
# UPDATE JOB STATUS
# -----------------------
@app.patch("/jobs/{job_id}", response_model=JobResponse)
def update_job_status(job_id: int, request: StatusUpdateRequest):
    jobs = load_jobs()

    for job in jobs:
        if job["id"] == job_id:
            job["status"] = request.status
            update_job(job_id, request.status)
            return job

    raise HTTPException(status_code=404, detail="Job not found")


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

    # 4. Create job entry
    job_entry = {
        "company": request.company,
        "role": request.role,
        "jd_file": jd_path,
        "resume_version": resume_path,
        "status": "generated",
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "edited": False,
        "notes": ""
    }

    add_job(job_entry)

    return {
        "message": "Resume generated successfully",
        "resume_path": resume_path
    }