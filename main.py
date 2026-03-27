import re
import os
import datetime
import subprocess
from dotenv import load_dotenv

from config import MODEL_NAME, JOBS_DIR
from services.ai_service import generate_resume
from services.resume_service import save_resume
from services.job_service import add_job

# -----------------------
# LOAD ENV
# -----------------------
load_dotenv()

# -----------------------
# READ INPUT FILES
# -----------------------
with open("master-resume.txt", "r") as f:
    resume = f.read()

with open("jd.txt", "r") as f:
    jd = f.read()

# -----------------------
# USER INPUT
# -----------------------
company = input("Enter company name: ")
role = input("Enter role: ")

# -----------------------
# GENERATE RESUME (AI SERVICE)
# -----------------------
try:
    resume_text = generate_resume(resume, jd)
except Exception as e:
    print("Error generating resume:", e)
    exit()

# -----------------------
# SAVE JD
# -----------------------
os.makedirs(JOBS_DIR, exist_ok=True)

company_slug = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')
jd_filename = f"{JOBS_DIR}/jd_{company_slug}.txt"

with open(jd_filename, "w") as f:
    f.write(jd)

# -----------------------
# SAVE RESUME (SERVICE)
# -----------------------
filename = save_resume(resume_text)

print(f"\nSaved to {filename}")

# -----------------------
# OPEN FILES IN VS CODE
# -----------------------
subprocess.run(["code", filename, jd_filename])

# -----------------------
# CREATE JOB ENTRY
# -----------------------
job_entry = {
    "company": company,
    "role": role,
    "jd_file": jd_filename,
    "resume_version": filename,
    "status": "generated",
    "date": datetime.datetime.now().strftime("%Y-%m-%d"),
    "edited": False,
    "notes": ""
}

# -----------------------
# SAVE JOB (SERVICE)
# -----------------------
add_job(job_entry)

print("Job saved to jobs.json")