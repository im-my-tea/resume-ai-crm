from google import genai
from dotenv import load_dotenv
from config import MODEL_NAME

# load env
load_dotenv()

# create client once
client = genai.Client()


def generate_resume(master_resume: str, jd_text: str) -> str:
    """
    Generate tailored resume text using Gemini
    """

    prompt = f"""
You are an expert resume optimizer.

Rewrite the resume to match the job description.

STRICT RULES:
- Output ONLY the final resume
- DO NOT explain changes
- DO NOT include commentary
- DO NOT include notes
- DO NOT include sections like "what was changed"
- Keep it clean and ready to send

Guidelines:
- Keep it truthful
- Improve wording and impact
- Align with job keywords
- Keep structure professional

--- RESUME ---
{master_resume}

--- JOB DESCRIPTION ---
{jd_text}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

    except Exception as e:
        raise Exception(f"AI generation failed: {str(e)}")