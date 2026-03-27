import os
import datetime
from config import VERSIONS_DIR

def save_resume(content):
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{VERSIONS_DIR}/resume_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write(content)

    return filename