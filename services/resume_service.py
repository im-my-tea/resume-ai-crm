import os
import datetime
from config import VERSIONS_DIR, GCS_BUCKET_NAME, USE_CLOUD


def save_resume(content: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{VERSIONS_DIR}/resume_{timestamp}.txt"

    if USE_CLOUD:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type="text/plain")
    else:
        os.makedirs(VERSIONS_DIR, exist_ok=True)
        with open(filename, "w") as f:
            f.write(content)

    return filename
