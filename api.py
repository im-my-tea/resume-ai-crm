from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import re
import os

from services.ai_service import generate_resume
from services.resume_service import save_resume
from services.job_service import add_job, load_jobs, update_job
from config import JOBS_DIR

app = FastAPI()


# -----------------------
# REQUEST SCHEMA
# -----------------------
class ResumeRequest(BaseModel):
    company: str
    role: str
    jd_text: str
    master_resume: str


class StatusUpdateRequest(BaseModel):
    status: str


# -----------------------
# ROOT
# -----------------------
@app.get("/")
def root():
    return {"message": "Resume AI CRM API running"}


# -----------------------
# GET ALL JOBS
# -----------------------
@app.get("/jobs")
def get_jobs():
    return load_jobs()


# -----------------------
# GET SINGLE JOB
# -----------------------
@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    jobs = load_jobs()

    if job_id < 0 or job_id >= len(jobs):
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]


# -----------------------
# UPDATE JOB STATUS
# -----------------------
@app.patch("/jobs/{job_id}")
def update_job_status(job_id: int, request: StatusUpdateRequest):
    jobs = load_jobs()

    if job_id < 0 or job_id >= len(jobs):
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    job["status"] = request.status

    update_job(job_id, job)

    return {"message": "Job updated successfully"}


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