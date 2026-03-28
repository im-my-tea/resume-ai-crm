import os
import subprocess

from services.job_service import load_jobs, update_job, get_job

while True:
    print("\n==== Resume AI CRM ====\n")
    print("1. Generate Resume")
    print("2. View Jobs")
    print("3. Update Status")
    print("4. View Job Details")
    print("5. Open Resume")
    print("6. Exit")

    choice = input("\nEnter choice: ")

    # -----------------------
    # GENERATE RESUME
    # -----------------------
    if choice == "1":
        os.system("python main.py")

    # -----------------------
    # VIEW JOBS (DB)
    # -----------------------
    elif choice == "2":
        jobs = load_jobs()

        if not jobs:
            print("\nNo jobs found.")
        else:
            print("\nYour Job Applications:\n")
            print("ID  Company        Role        Status     Edited  Date")
            print("--  ------------   ----------  ---------  ------  ----------")

            for job in jobs:
                print(
                    f"{job['id']:<3} "
                    f"{job['company']:<14} "
                    f"{job['role']:<10} "
                    f"{job['status']:<10} "
                    f"{str(job['edited']):<7} "
                    f"{job['date']}"
                )

    # -----------------------
    # UPDATE STATUS (DB)
    # -----------------------
    elif choice == "3":
        job_id = int(input("Enter job ID: "))

        print("\nSelect new status:")
        print("1. generated")
        print("2. applied")
        print("3. interview")
        print("4. rejected")
        print("5. offer")

        status_choice = input("Enter choice: ")

        status_map = {
            "1": "generated",
            "2": "applied",
            "3": "interview",
            "4": "rejected",
            "5": "offer"
        }

        status = status_map.get(status_choice)

        if not status:
            print("Invalid choice")
        else:
            update_job(job_id, status)
            print("Status updated.")

    # -----------------------
    # VIEW JOB DETAILS (DB)
    # -----------------------
    elif choice == "4":
        job_id = int(input("Enter job ID: "))
        job = get_job(job_id)

        if not job:
            print("Job not found.")
        else:
            print("\n==== Job Details ====\n")
            print(f"Company     : {job['company']}")
            print(f"Role        : {job['role']}")
            print(f"Status      : {job['status']}")
            print(f"Edited      : {job['edited']}")
            print(f"Date        : {job['date']}")
            print(f"Resume Path : {job['resume_path']}")
            print(f"JD Path     : {job['jd_path']}")
            print(f"Notes       : {job['notes']}")

            # show JD preview
            try:
                print("\n--- JD Preview ---\n")
                with open(job["jd_path"], "r") as f:
                    print(f.read()[:500])
            except:
                print("Could not load JD.")

    # -----------------------
    # OPEN RESUME
    # -----------------------
    elif choice == "5":
        job_id = int(input("Enter job ID: "))
        job = get_job(job_id)

        if not job:
            print("Job not found.")
        else:
            subprocess.run(["code", job["resume_path"]])

    # -----------------------
    # EXIT
    # -----------------------
    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid choice")