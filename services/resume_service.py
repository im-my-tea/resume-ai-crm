import os
import datetime
from config import VERSIONS_DIR, GCS_BUCKET_NAME, USE_CLOUD
from utils.logger import get_logger

logger = get_logger("resume_service")


def save_resume(content: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{VERSIONS_DIR}/resume_{timestamp}.txt"
    logger.info("save_resume started", extra={"filename": filename, "use_cloud": USE_CLOUD})
    try:
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
        logger.info("save_resume success", extra={"filename": filename})
        return filename
    except Exception:
        logger.error("save_resume failed", exc_info=True, extra={"filename": filename})
        raise
