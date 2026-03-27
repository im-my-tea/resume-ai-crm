import json
import subprocess

# load jobs
try:
    with open("jobs.json", "r") as f:
        jobs = json.load(f)
except:
    print("No jobs found.")
    exit()

if not jobs:
    print("No jobs to display.")
    exit()

print("\nYour Job Applications:\n")
print(f"{'ID':<3} {'Company':<20} {'Role':<20} {'Status':<12} {'Edited':<8} {'Date'}")
print("-" * 70)

for i, job in enumerate(jobs):
    edited = "Yes" if job.get("edited") else "No"
    print(f"{i:<3} {job['company']:<20} {job['role']:<20} {job['status']:<12} {edited:<8} {job['date']}")

# view jbs
def view_job_detail(index):
    import json

    try:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
    except:
        print("No jobs found.")
        return

    if index < 0 or index >= len(jobs):
        print("Invalid job index.")
        return

    job = jobs[index]

    print("\n===== Job Details =====\n")
    print(f"Company       : {job.get('company')}")
    print(f"Role          : {job.get('role')}")
    print(f"Status        : {job.get('status')}")
    print(f"Edited        : {'Yes' if job.get('edited') else 'No'}")
    print(f"Date          : {job.get('date')}")
    print(f"Resume Path   : {job.get('resume_version')}")
    print(f"JD Path       : {job.get('jd_file')}")

    # notes
    notes = job.get("notes", "")
    print(f"Notes         : {notes if notes else 'None'}")

    # jd preview 
    try:
        with open(job.get("jd_file"), "r") as f:
            print("\n--- JD Preview ---")
            for _ in range(5):
                line = f.readline()
                if not line:
                    break
                print(line.strip())
    except:
        print("\n(JD preview unavailable)")

#oepn cv
def open_resume(index):
    import json

    try:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
    except:
        print("No jobs found.")
        return

    if index < 0 or index >= len(jobs):
        print("Invalid job index.")
        return

    resume_path = jobs[index].get("resume_version")

    if not resume_path:
        print("No resume found.")
        return

    print(f"Opening: {resume_path}")
    subprocess.run(["code", resume_path])