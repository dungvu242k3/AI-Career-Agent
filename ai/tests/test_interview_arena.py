"""Unit tests for Adversarial Multi-Agent Mock Interview Arena Engine."""

import pytest
from ai.analysis.interview_arena import InterviewArenaEngine, TECH_LEAD_ALEX, HR_MANAGER_SARAH
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy, CVMetadata
from ai.models.interview import InterviewTurn, QuestionItem


@pytest.fixture
def candidate_profile():
    return CandidateProfile(
        personal_info=PersonalInfo(full_name="Trần Văn C"),
        summary=SummarySection(detected_title="Senior Python Backend Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python"],
            frameworks=["FastAPI"],
            databases=["PostgreSQL", "Redis"],
            devops_and_cloud=["Docker", "Kafka"],
        ),
        metadata=CVMetadata(total_experience_years=4.0),
    )


def test_start_session_creates_balanced_interviewer_turns(candidate_profile):
    """Verify that the engine generates questions from both Tech Lead Alex and HR Sarah."""
    engine = InterviewArenaEngine()
    session = engine.start_session(
        candidate_profile=candidate_profile,
        target_role="Senior Backend Engineer",
    )

    assert session.session_id.startswith("session-")
    assert session.candidate_name == "Trần Văn C"
    assert len(session.turns) >= 4

    # Verify personas present in the session
    interviewers = [t.question.interviewer.name for t in session.turns]
    assert "Alex" in interviewers
    assert "Sarah" in interviewers


def test_evaluate_turn_answer_scores_accurately(candidate_profile):
    """Verify that Silent Judge correctly scores STAR structure and technical terms."""
    engine = InterviewArenaEngine()
    session = engine.start_session(candidate_profile=candidate_profile)
    first_turn = session.turns[0]

    good_answer = (
        "Trong dự án fintech trước đây khi traffic tăng đột biến 5x, tôi đã thiết kế kiến trúc caching đa tầng với Redis cluster. "
        "Chúng tôi triển khai Rate Limiting và bất đồng bộ hóa ghi database qua Kafka queue. "
        "Kết quả là hệ thống giảm 60% latency và duy trì 99.9% uptime mà không bị sập Database."
    )

    evaluation = engine.evaluate_turn_answer(first_turn, good_answer)

    assert evaluation.score >= 85
    assert evaluation.technical_depth_score >= 20
    assert evaluation.star_structure_score >= 20
    assert len(evaluation.key_strengths) > 0
    assert "Harvard STAR" in evaluation.ideal_star_answer


def test_generate_final_assessment_compiles_report(candidate_profile):
    """Verify compilation of the post-interview hiring verdict and growth areas."""
    engine = InterviewArenaEngine()
    session = engine.start_session(candidate_profile=candidate_profile)

    for turn in session.turns:
        turn.candidate_answer = (
            "Trong dự án trước khi hệ thống tăng tải, tôi đã triển khai Redis caching và bất đồng bộ hóa với Kafka queue. "
            "Kết quả là hệ thống giảm 50% độ trễ API và duy trì 99.9% uptime mà không bị sập Database."
        )
        turn.evaluation = engine.evaluate_turn_answer(turn, turn.candidate_answer)

    report = engine.generate_final_assessment(session)

    assert report.total_turns_completed == len(session.turns)
    assert report.overall_score >= 70
    assert len(report.top_strengths) > 0
    assert len(report.actionable_prep_tips) > 0
