"""CV Analyzer Service — Score CV using ATS rubric and provide recommendations via Gemini."""

import json
from pathlib import Path

from google import genai
from google.genai import types

from config import get_settings
from models.candidate import CandidateProfile
from models.analysis import AnalysisReport

PROMPT_TEMPLATE = (Path(__file__).parent.parent / "prompts" / "analyze_cv.txt").read_text(
    encoding="utf-8"
)


def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


async def analyze_cv(profile: CandidateProfile) -> AnalysisReport:
    """Analyze a candidate profile and return ATS score with recommendations.

    Args:
        profile: Structured candidate profile from CV extraction.

    Returns:
        AnalysisReport with scores, skill gaps, and improvement suggestions.

    Raises:
        ValueError: If analysis fails or returns invalid data.
    """
    settings = get_settings()
    client = _get_client()

    profile_json = profile.model_dump_json(indent=2)
    prompt = PROMPT_TEMPLATE.replace("{profile_json}", profile_json)

    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
            max_output_tokens=8192,
            thinking_config=types.ThinkingConfig(thinking_budget=2048),
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned empty response for CV analysis")

    try:
        data = json.loads(response.text)
        report = AnalysisReport.model_validate(data)
        return report
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"Failed to parse CV analysis result: {e}")
