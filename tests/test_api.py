import re
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest

from services.ai_service import CircuitState, _breaker


UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@pytest.fixture(autouse=True)
def reset_breaker():
    """Reset the module-level breaker before and after every test."""
    _breaker._state = CircuitState.CLOSED
    _breaker._failure_count = 0
    _breaker._opened_at = None
    yield
    _breaker._state = CircuitState.CLOSED
    _breaker._failure_count = 0
    _breaker._opened_at = None


# 1. Valid input → 200
@patch("api.add_job")
@patch("api.save_resume", return_value="CVs/fake_path.txt")
@patch("api.generate_resume", return_value="fake resume text")
def test_generate_resume_success(mock_gen, mock_save, mock_add, client):
    payload = {
        "company": "Acme",
        "role": "Engineer",
        "jd_text": "x" * 100,
        "master_resume": "y" * 100,
    }
    r = client.post("/generate-resume", json=payload)
    assert r.status_code == 200
    assert r.json()["resume_path"] == "CVs/fake_path.txt"
    mock_gen.assert_called_once()
    mock_save.assert_called_once()
    mock_add.assert_called_once()


# 2. Invalid input → 422
def test_generate_resume_invalid_input(client):
    payload = {
        "company": "Acme",
        "role": "Engineer",
        "jd_text": "",
        "master_resume": "",
    }
    r = client.post("/generate-resume", json=payload)
    assert r.status_code == 422
    detail = r.json()["detail"]
    failed_fields = {tuple(err["loc"]) for err in detail}
    assert ("body", "jd_text") in failed_fields
    assert ("body", "master_resume") in failed_fields


# 3. /health structure (local mode: DB mocked, GCS skipped)
def test_health_ok(client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor

    with patch("api.get_connection", return_value=mock_conn), \
         patch("api.USE_CLOUD", False):
        r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "checks" in body
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["gcs"] == "skipped"


# 4. CircuitOpenError → 503 degraded JSON
def test_generate_resume_circuit_open(client):
    _breaker._state = CircuitState.OPEN
    _breaker._opened_at = time.monotonic()  # fresh cooldown — still OPEN

    payload = {
        "company": "Acme",
        "role": "Engineer",
        "jd_text": "x" * 100,
        "master_resume": "y" * 100,
    }
    r = client.post("/generate-resume", json=payload)
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "degraded"
    assert body["job"] == {"company": "Acme", "role": "Engineer"}


# 5. X-Request-ID header is a UUID4
def test_request_id_header(client):
    with patch("api.load_jobs", return_value=[]):
        r = client.get("/")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    rid = r.headers["X-Request-ID"]
    assert UUID4_RE.match(rid), rid
    parsed = uuid.UUID(rid)
    assert parsed.version == 4
