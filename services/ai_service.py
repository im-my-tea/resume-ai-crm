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
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

    except Exception as e:
        raise Exception(f"AI generation failed: {str(e)}")