"""Tests for Reflective Harvard Synthesizer Actor-Critic loop."""

import pytest
from unittest.mock import AsyncMock, patch
from ai.analysis.reflective_synthesizer import ReflectiveHarvardSynthesizer
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy
from ai.models.harvard_cv import HarvardCVData, HarvardContactInfo, HarvardExperienceItem, HarvardSkillsCategory
from ai.models.jd import JDProfile, JDMatchReport


@pytest.fixture
def mock_candidate_and_jd():
    cand = CandidateProfile(
        personal_info=PersonalInfo(full_name="Lê Minh B"),
        summary=SummarySection(detected_title="Frontend Engineer"),
        skills_taxonomy=SkillsTaxonomy(languages_and_frameworks=["React", "TypeScript", "Next.js"]),
    )
    jd = JDProfile(
        job_title="Senior Frontend Developer",
        must_have_skills=["React", "TypeScript", "Next.js"],
        raw_text="Tuyển Senior Frontend React",
    )
    report = JDMatchReport(
        overall_score=85,
        skill_match_score=90,
        experience_fit_score=80,
        format_quality_score=85,
        matched_skills=[],
        missing_skills=[],
        excess_skills=[],
    )
    return cand, jd, report


@pytest.mark.asyncio
async def test_reflective_synthesizer_converges(mock_candidate_and_jd):
    """Test that the Reflective Synthesizer executes Actor -> Critic and converges."""
    cand, jd, report = mock_candidate_and_jd

    mock_initial_cv = HarvardCVData(
        target_language="vi",
        target_role="Senior Frontend Developer",
        contact=HarvardContactInfo(full_name="Lê Minh B"),
        experience=[
            HarvardExperienceItem(
                company="Shopee",
                role="Frontend Developer",
                date_range="2022 - Present",
                bullets=[
                    "Tham gia vào phát triển giao diện web với React và TypeScript.",
                ],
            )
        ],
        skills_categories=[
            HarvardSkillsCategory(category_name="Frontend", skills=["React", "TypeScript", "Next.js"])
        ],
    )

    synthesizer = ReflectiveHarvardSynthesizer(max_iterations=3, approval_threshold=80)

    with patch.object(synthesizer.actor_synthesizer, "synthesize", new=AsyncMock(return_value=mock_initial_cv)):
        final_cv, reflection_result = await synthesizer.synthesize(
            profile=cand,
            jd=jd,
            report=report,
        )

        assert reflection_result.iterations_count >= 1
        assert reflection_result.final_critic_score >= 80
        assert len(reflection_result.reflection_history) >= 1
        # Check that passive starter was rewritten with an Action Verb
        first_bullet = final_cv.experience[0].bullets[0]
        assert not first_bullet.startswith("Tham gia vào")
