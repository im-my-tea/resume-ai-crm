import re
import os
import tempfile
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

# -----------------------
# JD INPUT (EDITOR FLOW)
# -----------------------

print("\nPaste JD in the opened file, save it, then come back.\n")

# create temp file
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
    temp_jd_path = tmp.name

# open in VS Code
subprocess.run(["code", temp_jd_path])

input("Press Enter after pasting JD and saving file...")

# read JD
with open(temp_jd_path, "r") as f:
    jd = f.read()

# basic validation
if not jd.strip():
    print("JD is empty. Exiting.")
    exit()

# -----------------------
# USER INPUT
# -----------------------
company = input("Enter company name: ")
role = input("Enter role: ")

# -----------------------
# GENERATE RESUME (AI SERVICE)
# -----------------------
try:
    print("Waiting for API response ... ")
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
os.remove(temp_jd_path)
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
# SAVE JOB (SERVICE)
# -----------------------
add_job(company, role, jd_filename, filename)

print("Job saved to DB!")