import datetime
import psycopg2.extras
from config import USE_CLOUD
from db.database import get_connection


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
    conn = get_connection()
    if USE_CLOUD:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    rows = _fetchall(cursor)
    conn.close()
    return rows


def get_job(job_id: int):
    conn = get_connection()
    if USE_CLOUD:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = %s" if USE_CLOUD else "SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = _fetchone(cursor)
    conn.close()
    return row


def update_job(job_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    ph = "%s" if USE_CLOUD else "?"
    cursor.execute(f"UPDATE jobs SET status = {ph} WHERE id = {ph}", (status, job_id))
    conn.commit()
    conn.close()


def update_notes(job_id: int, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    ph = "%s" if USE_CLOUD else "?"
    cursor.execute(f"UPDATE jobs SET notes = {ph} WHERE id = {ph}", (notes, job_id))
    conn.commit()
    conn.close()


def delete_job(job_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    ph = "%s" if USE_CLOUD else "?"
    cursor.execute(f"DELETE FROM jobs WHERE id = {ph}", (job_id,))
    conn.commit()
    conn.close()


def add_job(company: str, role: str, jd_path: str, resume_path: str):
    conn = get_connection()
    cursor = conn.cursor()
    ph = "%s" if USE_CLOUD else "?"
    cursor.execute(
        f"INSERT INTO jobs (company, role, jd_path, resume_path, status, date, edited, notes) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
        (company, role, jd_path, resume_path, "generated", datetime.date.today().isoformat(), False, None)
    )
    conn.commit()
    conn.close()
