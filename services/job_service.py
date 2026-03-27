import json
import os
import datetime

JOBS_FILE = "jobs.json"

def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def add_job(job_entry):
    jobs = load_jobs()
    jobs.append(job_entry)
    save_jobs(jobs)

def update_job(index, updated_job):
    jobs = load_jobs()
    jobs[index] = updated_job
    save_jobs(jobs)