FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p CVs JDs data
RUN python -c "import sqlite3; conn = sqlite3.connect('data/jobs.db'); conn.executescript(open('db/schema.sql').read()); conn.commit(); conn.close()"
EXPOSE 8080
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
