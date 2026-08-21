"""Tests for grounded actor/critic CV synthesis."""

from unittest.mock import AsyncMock, patch

import pytest

from ai.analysis.reflective_synthesizer import ReflectiveHarvardSynthesizer
from ai.models.candidate import CandidateProfile, PersonalInfo, SkillsTaxonomy, SummarySection
from ai.models.harvard_cv import HarvardCVData, HarvardContactInfo, HarvardExperienceItem, HarvardSkillsCategory
from ai.models.jd import JDMatchReport, JDProfile


@pytest.mark.asyncio
async def test_reflection_drops_experience_without_source_evidence():
    profile = CandidateProfile(
        personal_info=PersonalInfo(full_name="Candidate"),
        summary=SummarySection(detected_title="Frontend Engineer"),
        skills_taxonomy=SkillsTaxonomy(frameworks=["React"]),
    )
    jd = JDProfile(job_title="Senior Frontend Developer", raw_text="React role")
    report = JDMatchReport(
        overall_score=85,
        skill_match_score=90,
        experience_fit_score=80,
        format_quality_score=85,
    )
    ungrounded = HarvardCVData(
        target_language="vi",
        target_role="Senior Frontend Developer",
        contact=HarvardContactInfo(full_name="Candidate"),
        experience=[
            HarvardExperienceItem(
                company="Unknown",
                role="Frontend Developer",
                date_range="2022 - Present",
                bullets=["Improved latency by 30%"],
            )
        ],
        skills_categories=[HarvardSkillsCategory(category_name="Frontend", skills=["React", "UnknownSkill"])],
    )
    synthesizer = ReflectiveHarvardSynthesizer(max_iterations=2, approval_threshold=80)
    with patch.object(synthesizer.actor_synthesizer, "synthesize", new=AsyncMock(return_value=ungrounded)):
        final_cv, result = await synthesizer.synthesize(profile, jd, report)

    assert not final_cv.experience
    assert final_cv.ats_score_estimate == 85
    assert "experience:Unknown/Frontend Developer" in result.grounding_report["dropped_claims"]
    assert "skill:UnknownSkill" in result.grounding_report["dropped_claims"]
