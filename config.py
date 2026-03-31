import os

MODEL_NAME = "gemini-2.5-flash"

# File storage (local)
VERSIONS_DIR = "CVs"
JOBS_DIR = "JDs"

# Database (local)
DB_PATH = "data/jobs.db"

# Cloud SQL (Postgres) — only used when DATABASE_URL is set
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# GCS — only used in cloud mode
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# Mode detection — if DATABASE_URL is set, run in cloud mode
USE_CLOUD = os.environ.get("DATABASE_URL") is not None