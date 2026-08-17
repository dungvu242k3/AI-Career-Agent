"""CV Extractor Service — Convert raw CV text to structured CandidateProfile using Gemini."""

import json
from pathlib import Path

from google import genai
from google.genai import types

from config import get_settings
from models.candidate import CandidateProfile

PROMPT_TEMPLATE = (Path(__file__).parent.parent / "prompts" / "extract_cv.txt").read_text(
    encoding="utf-8"
)


def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


async def extract_profile(cv_text: str) -> CandidateProfile:
    """Extract structured candidate profile from raw CV text.

    Args:
        cv_text: Raw text extracted from CV PDF.

    Returns:
        CandidateProfile with all extracted information.

    Raises:
        ValueError: If extraction fails or returns invalid data.
    """
    settings = get_settings()
    client = _get_client()

    prompt = PROMPT_TEMPLATE.replace("{cv_text}", cv_text)

    response = client.models.generate_content(
        model=settings.gemini_flash_lite_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=4096,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned empty response for CV extraction")

    try:
        data = json.loads(response.text)
        profile = CandidateProfile.model_validate(data)
        return profile
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"Failed to parse CV extraction result: {e}")
