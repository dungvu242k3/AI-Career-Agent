"""Unit tests for OpenAICVExtractor with mocked OpenAI client."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from ai.extractors.openai_extractor import OpenAICVExtractor
from ai.models.candidate import (
    CandidateProfile,
    PersonalInfo,
    SkillsTaxonomy,
    SummarySection,
    WorkExperienceItem,
)


@pytest.mark.asyncio
async def test_openai_extractor_parse_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()

    sample_parsed = CandidateProfile(
        personal_info=PersonalInfo(
            full_name="Hoang Van OpenAI",
            email="hoang@openai.test",
            phone="0987654321",
            linkedin_url="linkedin.com/in/hoangtest",
        ),
        summary=SummarySection(detected_title="Senior AI Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python", "python", "TypeScript"],
        ),
        work_experience=[
            WorkExperienceItem(
                company="OpenAI Corp",
                role="Engineer",
                start_date="2022-01",
                end_date="2024-01",
                raw_bullets=["Built GPT-4 structured outputs"],
            )
        ],
    )

    mock_message.parsed = sample_parsed
    mock_message.refusal = None
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_response)

    extractor = OpenAICVExtractor(client=mock_client)
    profile = await extractor.extract_profile("Hoang Van OpenAI - Resume text...")

    assert profile.full_name == "Hoang Van OpenAI"
    assert profile.title == "Senior AI Engineer"
    assert profile.personal_info.linkedin_url == "https://linkedin.com/in/hoangtest"
    assert profile.skills_taxonomy.programming_languages == ["Python", "TypeScript"]
    assert profile.metadata.total_experience_years == 2.1


@pytest.mark.asyncio
async def test_openai_extractor_handles_api_exception():
    mock_client = MagicMock()
    mock_client.beta.chat.completions.parse = AsyncMock(
        side_effect=Exception("Rate limit exceeded")
    )

    extractor = OpenAICVExtractor(client=mock_client)
    with pytest.raises(ValueError) as exc_info:
        await extractor.extract_profile("CV content")

    assert "OpenAI API" in str(exc_info.value)
