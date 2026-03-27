import re
import os
import json
import datetime
import subprocess
from dotenv import load_dotenv
from google import genai

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

# take user input
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
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

# -----------------------
# SAVE JD PER JOB (NEW)
# -----------------------

# create jobs folder
os.makedirs("jobs", exist_ok=True)

# safe filename (no spaces) - upgraded w re later
company_slug = re.sub(r'[^a-z0-9]+', '-', company.lower()).strip('-')

jd_filename = f"jobs/jd_{company_slug}.txt"

with open(jd_filename, "w") as f:
    f.write(jd)

# -----------------------
# SAVE VERSION
# -----------------------
os.makedirs("versions", exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
filename = f"versions/resume_{timestamp}.txt"

with open(filename, "w") as f:
    f.write(response.text)

print(f"\nSaved to {filename}")

# -----------------------
# OPEN IN VS CODE
# -----------------------
subprocess.run(["code", filename, jd_filename])

# -----------------------
# JOB TRACKING (NEW)
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

# load existing jobs
if os.path.exists("jobs.json"):
    with open("jobs.json", "r") as f:
        try:
            jobs = json.load(f)
        except:
            jobs = []
else:
    jobs = []

# append new job
jobs.append(job_entry)

# save updated jobs
with open("jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)

print("Job saved to jobs.json")