import sqlite3
from config import DB_PATH


def load_jobs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_job(job_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)
    return None


def update_job(job_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE jobs SET status = ? WHERE id = ?",
        (status, job_id)
    )

    conn.commit()
    conn.close()


def add_job(company: str, role: str, jd_path: str, resume_path: str):
    import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO jobs (company, role, jd_path, resume_path, status, date, edited, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (company, role, jd_path, resume_path, "generated", datetime.date.today().isoformat(), False, None)
    )

    conn.commit()
    conn.close()