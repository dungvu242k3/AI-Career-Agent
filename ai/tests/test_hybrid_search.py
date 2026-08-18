"""Unit tests for Hybrid Dense-Sparse Job Search Engine."""

import pytest
from ai.analysis.hybrid_search import HybridJobSearchEngine
from ai.analysis.job_embeddings import JobEmbeddingEngine, compute_cosine_similarity
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy


@pytest.fixture
def mock_jobs():
    return [
        {
            "id": "job-1",
            "title": "Senior Python Backend Engineer",
            "domain": "backend",
            "min_experience_years": 3.0,
            "max_experience_years": 6.0,
            "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka"],
            "requirements": ["3+ years in Python", "Experience with Redis caching and microservices"],
            "description": "High-throughput financial backend services.",
        },
        {
            "id": "job-2",
            "title": "Frontend Developer (React / Next.js)",
            "domain": "frontend",
            "min_experience_years": 2.0,
            "max_experience_years": 4.0,
            "tech_stack": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
            "requirements": ["2+ years React and modern CSS"],
            "description": "Building interactive user interfaces.",
        },
        {
            "id": "job-3",
            "title": "DevOps Engineer (AWS / Kubernetes)",
            "domain": "devops",
            "min_experience_years": 3.0,
            "max_experience_years": 6.0,
            "tech_stack": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD"],
            "requirements": ["Kubernetes and infrastructure as code"],
            "description": "Scaling cloud infrastructure.",
        },
    ]


@pytest.fixture
def candidate_backend_profile():
    return CandidateProfile(
        personal_info=PersonalInfo(full_name="Nguyễn Văn A"),
        summary=SummarySection(detected_title="Senior Python Backend Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python"],
            frameworks=["FastAPI", "Django"],
            databases=["PostgreSQL", "Redis"],
            devops_and_cloud=["Kafka"],
        ),
    )


def test_embedding_engine_cosine_similarity():
    """Verify vector projection and similarity calculations."""
    engine = JobEmbeddingEngine(vector_dim=64)
    v1 = engine.generate_text_vector("FastAPI Python Backend Microservices")
    v2 = engine.generate_text_vector("Python FastAPI Redis Backend")
    v3 = engine.generate_text_vector("Flutter Android iOS Mobile")

    sim_12 = compute_cosine_similarity(v1, v2)
    sim_13 = compute_cosine_similarity(v1, v3)

    assert sim_12 > sim_13
    assert sim_12 > 0.4


def test_hybrid_search_ranks_relevant_domain_first(mock_jobs, candidate_backend_profile):
    """Test that a backend candidate matches the backend job at rank #1."""
    hybrid_engine = HybridJobSearchEngine()
    ranked = hybrid_engine.search_and_rank(
        jobs=mock_jobs,
        query="backend",
        candidate_profile=candidate_backend_profile,
    )

    assert len(ranked) == 3
    top_job, score = ranked[0]
    assert top_job["id"] == "job-1"
    assert top_job["domain"] == "backend"
    assert score > ranked[1][1]
