from fastapi import FastAPI
from services.job_service import load_jobs

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Resume AI CRM API running"}

@app.get("/jobs")
def get_jobs():
    return load_jobs()