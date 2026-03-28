CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    role TEXT,
    jd_path TEXT,
    resume_path TEXT,
    status TEXT,
    date TEXT,
    edited BOOLEAN,
    notes TEXT
);