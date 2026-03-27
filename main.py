import re
import os
import datetime
import subprocess
from dotenv import load_dotenv
from google import genai
from config import MODEL_NAME, JOBS_DIR
from services.resume_service import save_resume
from services.job_service import add_job

# -----------------------
# LOAD ENV + CLIENT
# -----------------------
load_dotenv()
client = genai.Client()

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
# BUILD PROMPT
# -----------------------
prompt = f"""
You are an expert resume optimizer.

Rewrite the resume to match the job description.

STRICT RULES:
- Output ONLY the final resume
- DO NOT explain changes
- DO NOT include commentary
- DO NOT include notes
- DO NOT include sections like "what was changed"
- Keep it clean and ready to send

Guidelines:
- Keep it truthful
- Improve wording and impact
- Align with job keywords
- Keep structure professional

--- RESUME ---
{resume}

--- JOB DESCRIPTION ---
{jd}
"""

# -----------------------
# CALL GEMINI
# -----------------------
try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
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
# SAVE RESUME (via service)
# -----------------------
filename = save_resume(response.text)

print(f"\nSaved to {filename}")

# -----------------------
# OPEN FILES
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
# SAVE JOB (via service)
# -----------------------
add_job(job_entry)

print("Job saved to jobs.json")