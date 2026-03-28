import datetime
from db.database import get_connection


# -------------------------
# CREATE JOB
# -------------------------
def add_job(company, role, jd_path, resume_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (company, role, jd_path, resume_path, status, date, edited, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        role,
        jd_path,
        resume_path,
        "generated",
        datetime.date.today().isoformat(),
        0,
        ""
    ))

    conn.commit()
    conn.close()


# -------------------------
# GET ALL JOBS
# -------------------------
def load_jobs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    conn.close()

    jobs = []
    for row in rows:
        jobs.append({
            "id": row[0],
            "company": row[1],
            "role": row[2],
            "jd_path": row[3],
            "resume_path": row[4],
            "status": row[5],
            "date": row[6],
            "edited": bool(row[7]),
            "notes": row[8]
        })

    return jobs


# -------------------------
# UPDATE JOB STATUS
# -------------------------
def update_job(job_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE jobs
        SET status = ?
        WHERE id = ?
    """, (status, job_id))

    conn.commit()
    conn.close()


# -------------------------
# GET SINGLE JOB
# -------------------------
def get_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "company": row[1],
        "role": row[2],
        "jd_path": row[3],
        "resume_path": row[4],
        "status": row[5],
        "date": row[6],
        "edited": bool(row[7]),
        "notes": row[8]
    }