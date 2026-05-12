import datetime
import os
import re
import time
import uuid
from typing import List, Literal, Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from config import GCS_BUCKET_NAME, JOBS_DIR, USE_CLOUD
from db.database import get_connection
from services.ai_service import generate_resume
from services.job_service import (
    add_job,
    delete_job,
    get_job,
    load_jobs,
    update_job,
    update_notes,
)
from services.resume_service import save_resume
from utils.logger import get_logger

app = FastAPI()
logger = get_logger("api")
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
    status: Literal["generated", "applied", "interview", "rejected", "offer"]


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


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    method = request.method
    path = request.url.path
    logger.info(
        "Request started",
        extra={"request_id": request_id, "method": method, "path": path},
    )
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.error(
            "Request failed",
            exc_info=True,
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "duration_ms": duration_ms,
            },
        )
        raise
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.get("/healthz")
def healthz():
    checks = {}

    # Database check: SELECT 1
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        finally:
            conn.close()
        checks["database"] = "ok"
        logger.info("healthz database check passed")
    except Exception:
        checks["database"] = "fail"
        logger.error("healthz database check failed", exc_info=True)

    # GCS check: only when USE_CLOUD, otherwise mark skipped
    if USE_CLOUD:
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET_NAME)
            if not bucket.exists():
                raise Exception(f"bucket {GCS_BUCKET_NAME} not found")
            checks["gcs"] = "ok"
            logger.info("healthz gcs check passed", extra={"bucket": GCS_BUCKET_NAME})
        except Exception:
            checks["gcs"] = "fail"
            logger.error(
                "healthz gcs check failed",
                exc_info=True,
                extra={"bucket": GCS_BUCKET_NAME},
            )
    else:
        checks["gcs"] = "skipped"
        logger.info("healthz gcs check skipped", extra={"use_cloud": False})

    healthy = not any(v == "fail" for v in checks.values())
    body = {"status": "ok" if healthy else "degraded", "checks": checks}
    return JSONResponse(status_code=200 if healthy else 503, content=body)


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
        if USE_CLOUD:
            from google.cloud import storage

            client = storage.Client()
            blob = client.bucket(GCS_BUCKET_NAME).blob(job["resume_path"])
            resume_text = blob.download_as_text()
        else:
            with open(job["resume_path"], "r") as f:
                resume_text = f.read()
    except Exception:
        pass

    return templates.TemplateResponse(
        request,
        "job_detail.html",
        {"job": job, "job_id": job_id, "resume_text": resume_text},
    )


@app.post("/jobs/{job_id}/update")
def update_job_status_ui(job_id: int, status: str = Form(...)):
    update_job(job_id, status)

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


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
    master_resume: str = Form(...),
):
    resume_text = generate_resume(master_resume, jd_text)
    resume_path = save_resume(resume_text)
    company_slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    jd_path = f"{JOBS_DIR}/jd_{company_slug}.txt"
    if USE_CLOUD:
        from google.cloud import storage

        client = storage.Client()
        blob = client.bucket(GCS_BUCKET_NAME).blob(jd_path)
        blob.upload_from_string(jd_text, content_type="text/plain")
    else:
        os.makedirs(JOBS_DIR, exist_ok=True)
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
    resume_text = generate_resume(request.master_resume, request.jd_text)

    # 2. Save resume
    resume_path = save_resume(resume_text)

    # 3. Save JD
    company_slug = re.sub(r"[^a-z0-9]+", "-", request.company.lower()).strip("-")
    jd_path = f"{JOBS_DIR}/jd_{company_slug}.txt"

    if USE_CLOUD:
        from google.cloud import storage

        client = storage.Client()
        blob = client.bucket(GCS_BUCKET_NAME).blob(jd_path)
        blob.upload_from_string(request.jd_text, content_type="text/plain")
    else:
        os.makedirs(JOBS_DIR, exist_ok=True)
        with open(jd_path, "w") as f:
            f.write(request.jd_text)

    # 4. Save to DB (IMPORTANT FIX)
    add_job(request.company, request.role, jd_path, resume_path)

    return {"message": "Resume generated successfully", "resume_path": resume_path}
