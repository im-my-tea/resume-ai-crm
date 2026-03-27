import os

while True:
    print("\n==== Resume AI CRM ====\n")
    print("1. Generate Resume")
    print("2. View Jobs")
    print("3. Update Status")
    print("4. View Job Details")
    print("5. Open Resume")
    print("6. Exit")

    choice = input("\nEnter choice: ")

    if choice == "1":
        os.system("python main.py")

    elif choice == "2":
        os.system("python view_jobs.py")

    elif choice == "3":
        os.system("python update_status.py")

    elif choice == "4":
        import view_jobs
        index = int(input("Enter job ID: "))
        view_jobs.view_job_detail(index)

    elif choice == "5":
        import view_jobs
        index = int(input("Enter job ID: "))
        view_jobs.open_resume(index)

    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid choice")