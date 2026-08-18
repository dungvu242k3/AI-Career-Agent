"""Unit tests for JobCrossEncoderReranker."""

import pytest
from ai.analysis.job_reranker import JobCrossEncoderReranker
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy, CVMetadata


@pytest.fixture
def sample_candidate():
    return CandidateProfile(
        personal_info=PersonalInfo(full_name="Nguyễn Văn A"),
        summary=SummarySection(detected_title="Senior Python Backend Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python"],
            frameworks=["FastAPI"],
            databases=["PostgreSQL", "Redis"],
            devops_and_cloud=["Docker", "Kafka"],
        ),
        metadata=CVMetadata(total_experience_years=4.0),
    )


def test_job_reranker_scores_and_highlights(sample_candidate):
    """Test that the Cross-Encoder reranks jobs and attaches semantic fit score and highlights."""
    mock_ranked_jobs = [
        (
            {
                "id": "job-1",
                "title": "Senior Backend Developer",
                "domain": "backend",
                "min_experience_years": 3.0,
                "tech_stack": ["Python", "FastAPI", "Redis"],
            },
            0.85,
        ),
        (
            {
                "id": "job-2",
                "title": "Junior Frontend Developer",
                "domain": "frontend",
                "min_experience_years": 1.0,
                "tech_stack": ["React", "CSS"],
            },
            0.20,
        ),
    ]

    reranker = JobCrossEncoderReranker()
    reranked = reranker.rerank_top_k(
        candidate_profile=sample_candidate,
        ranked_jobs=mock_ranked_jobs,
        top_k=2,
    )

    assert len(reranked) == 2
    top = reranked[0]
    assert top["id"] == "job-1"
    assert top["semantic_fit_score"] >= 80
    assert len(top["fit_highlights"]) > 0
    assert "Khớp mạnh kỹ năng cốt lõi" in top["fit_highlights"][0]


def test_job_reranker_handles_job_item_schema_format(sample_candidate):
    """Test that JobItemSchema dicts with 'skills' and 'min_years_exp' are correctly processed."""
    job_item_dict = {
        "id": "job-schema-01",
        "title": "Backend Python Lead",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "min_years_exp": 3.0,
        "requirements": "• 3+ năm kinh nghiệm Python FastAPI",
        "description": "Lập trình backend",
    }

    reranker = JobCrossEncoderReranker()
    reranked = reranker.rerank_top_k(
        candidate_profile=sample_candidate,
        ranked_jobs=[(job_item_dict, 0.9)],
        top_k=1,
    )

    assert len(reranked) == 1
    assert reranked[0]["semantic_fit_score"] >= 85
    assert any("Khớp mạnh kỹ năng cốt lõi" in h for h in reranked[0]["fit_highlights"])
