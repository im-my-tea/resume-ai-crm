import json

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