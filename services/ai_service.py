import time
from enum import Enum
from threading import Lock

from dotenv import load_dotenv
from google import genai

from config import MODEL_NAME
from utils.logger import get_logger

# load env
load_dotenv()

# create client once
client = genai.Client()
logger = get_logger("ai_service")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when the circuit is open and a call is refused."""
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, cooldown: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: float | None = None
        self._lock = Lock()

    def _set_state(self, new_state: CircuitState) -> None:
        # caller holds self._lock
        if self._state is not new_state:
            self._state = new_state
            logger.info("Circuit breaker state changed", extra={"state": new_state.value})

    def before_call(self) -> None:
        """Gate a call. Raises CircuitOpenError if the breaker is open."""
        with self._lock:
            if self._state is CircuitState.OPEN:
                assert self._opened_at is not None
                if (time.monotonic() - self._opened_at) >= self.cooldown:
                    self._set_state(CircuitState.HALF_OPEN)
                else:
                    raise CircuitOpenError("Circuit breaker is open; refusing call")

    def record_success(self) -> None:
        with self._lock:
            self._failure_count = 0
            self._opened_at = None
            if self._state is not CircuitState.CLOSED:
                self._set_state(CircuitState.CLOSED)

    def record_failure(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                # probe failed — re-open and restart cooldown
                self._opened_at = time.monotonic()
                self._set_state(CircuitState.OPEN)
                return
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._opened_at = time.monotonic()
                self._set_state(CircuitState.OPEN)


# module-level singleton
_breaker = CircuitBreaker(failure_threshold=5, cooldown=60.0)


def generate_resume(master_resume: str, jd_text: str) -> str:
    """
    Generate tailored resume text using Gemini
    """
    logger.info("Starting resume generation")

    _breaker.before_call()  # raises CircuitOpenError if open

    prompt = f"""You are an expert resume optimizer helping a candidate tailor their resume for a specific job.

    Your task: rewrite the resume to better match the job description, without changing the underlying facts.

    RULES:
    - Output ONLY the final resume text. No commentary, no notes, no explanations.
    - Do not invent or add any experience, skill, project, or achievement not present in the original resume.
    - Preserve the original structure, section order, and formatting style exactly.
    - Use exact keywords and phrases from the job description where truthfully applicable (for ATS compatibility).
    - Strengthen the wording of existing bullet points to emphasize relevant impact.
    - Deprioritize or trim experiences that are irrelevant to this role.

    --- RESUME ---
    {master_resume}

    --- JOB DESCRIPTION ---
    {jd_text}
    """

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    except Exception as e:
        _breaker.record_failure()
        logger.error("Gemini API call failed", exc_info=True)
        raise Exception(f"AI generation failed: {str(e)}")

    _breaker.record_success()
    logger.info("Resume generation successful")
    return response.text
