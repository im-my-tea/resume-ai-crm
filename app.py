import os

while True:
    print("\n==== Resume AI CRM ====\n")
    print("1. Generate Resume")
    print("2. View Jobs")
    print("3. Update Status")
    print("4. Exit")

    choice = input("\nEnter choice: ")

    if choice == "1":
        os.system("python main.py")

    elif choice == "2":
        os.system("python view_jobs.py")

    elif choice == "3":
        os.system("python update_status.py")

    elif choice == "4":
        print("Exiting...")
        break

    else:
        print("Invalid choice")