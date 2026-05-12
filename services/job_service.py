import datetime
import psycopg2.extras
from config import USE_CLOUD
from db.database import get_connection
from utils.logger import get_logger

logger = get_logger("job_service")


def _fetchall(cursor):
    rows = cursor.fetchall()
    if USE_CLOUD:
        return rows  # already dicts via RealDictCursor
    return [dict(row) for row in rows]


def _fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    if USE_CLOUD:
        return dict(row)
    return dict(row)


def load_jobs():
    try:
        conn = get_connection()
        try:
            if USE_CLOUD:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs")
            return _fetchall(cursor)
        finally:
            conn.close()
    except Exception:
        logger.error("load_jobs failed", exc_info=True)
        raise


def get_job(job_id: int):
    try:
        conn = get_connection()
        try:
            if USE_CLOUD:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            else:
                cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = %s" if USE_CLOUD else "SELECT * FROM jobs WHERE id = ?", (job_id,))
            return _fetchone(cursor)
        finally:
            conn.close()
    except Exception:
        logger.error("get_job failed", exc_info=True, extra={"job_id": job_id})
        raise


def update_job(job_id: int, status: str):
    logger.info("update_job started", extra={"job_id": job_id, "status": status})
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = "%s" if USE_CLOUD else "?"
            cursor.execute(f"UPDATE jobs SET status = {ph} WHERE id = {ph}", (status, job_id))
            conn.commit()
        finally:
            conn.close()
        logger.info("update_job success", extra={"job_id": job_id, "status": status})
    except Exception:
        logger.error("update_job failed", exc_info=True, extra={"job_id": job_id, "status": status})
        raise


def update_notes(job_id: int, notes: str):
    logger.info("update_notes started", extra={"job_id": job_id})
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = "%s" if USE_CLOUD else "?"
            cursor.execute(f"UPDATE jobs SET notes = {ph} WHERE id = {ph}", (notes, job_id))
            conn.commit()
        finally:
            conn.close()
        logger.info("update_notes success", extra={"job_id": job_id})
    except Exception:
        logger.error("update_notes failed", exc_info=True, extra={"job_id": job_id})
        raise


def delete_job(job_id: int):
    logger.info("delete_job started", extra={"job_id": job_id})
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = "%s" if USE_CLOUD else "?"
            cursor.execute(f"DELETE FROM jobs WHERE id = {ph}", (job_id,))
            conn.commit()
        finally:
            conn.close()
        logger.info("delete_job success", extra={"job_id": job_id})
    except Exception:
        logger.error("delete_job failed", exc_info=True, extra={"job_id": job_id})
        raise


def add_job(company: str, role: str, jd_path: str, resume_path: str):
    logger.info("add_job started", extra={"company": company, "role": role})
    try:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = "%s" if USE_CLOUD else "?"
            cursor.execute(
                f"INSERT INTO jobs (company, role, jd_path, resume_path, status, date, edited, notes) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                (company, role, jd_path, resume_path, "generated", datetime.date.today().isoformat(), False, None)
            )
            conn.commit()
        finally:
            conn.close()
        logger.info("add_job success", extra={"company": company, "role": role})
    except Exception:
        logger.error("add_job failed", exc_info=True, extra={"company": company, "role": role})
        raise
