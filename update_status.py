import json

# load jobs
with open("jobs.json", "r") as f:
    jobs = json.load(f)

# check if empty
if not jobs:
    print("No jobs found.")
    exit()

# display jobs
print("\nYour Jobs:\n")
for i, job in enumerate(jobs):
    print(f"{i}. {job['company']} - {job['role']} [{job['status']}]")

# select job
index = int(input("\nEnter job number to update: "))

if index < 0 or index >= len(jobs):
    print("Invalid selection")
    exit()

# status options
statuses = ["generated", "applied", "oa", "interview1", "interview2", "offer", "rejected"]

print("\nSelect new status:")
for i, s in enumerate(statuses):
    print(f"{i}. {s}")

status_index = int(input("\nEnter status number: "))
new_status = statuses[status_index]

if status_index < 0 or status_index >= len(statuses):
    print("Invalid status")
    exit()

# update status
jobs[index]["status"] = new_status

# ask if resume edited
edited_input = input("Have you edited this resume? (y/n): ").lower()
if edited_input == "y":
    jobs[index]["edited"] = True

# add notes
notes = input("Add notes (or press enter to skip): ")
if notes.strip():
    jobs[index]["notes"] = notes

# save back
with open("jobs.json", "w") as f:
    json.dump(jobs, f, indent=2)

print("\nDetails updated successfully.")