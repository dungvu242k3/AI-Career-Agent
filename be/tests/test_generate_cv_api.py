"""Integration tests for Harvard 1-Page CV Generation API endpoint (POST /api/v1/ats/generate-cv)."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from ai.analysis.ats_matcher import ATSMatcher
from ai.analysis.harvard_synthesizer import HarvardCVSynthesizer
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, EducationItem, WorkExperienceItem, ProjectItem, SkillsTaxonomy
from ai.models.jd import JDMatchReport, JDProfile, SkillMatchItem
from ai.models.harvard_cv import HarvardCVData, HarvardContactInfo, HarvardEducationItem, HarvardExperienceItem, HarvardProjectItem, HarvardSkillsCategory, HarvardCertAndLangSection
from ai.parsers.jd_parser import JDParser
from be.api.v1.ats_router import (
    get_cached_ats_matcher,
    get_cached_jd_parser,
    get_cached_harvard_synthesizer,
)
from be.core.rate_limiter import (
    upload_rate_limiter,
    read_rate_limiter,
    ats_rate_limiter,
    star_rate_limiter,
    cv_generation_rate_limiter,
)
from be.db.database import save_candidate
from be.main import app


class MockJDParser(JDParser):
    async def parse_jd_text(self, raw_text: str) -> JDProfile:
        return JDProfile(
            job_title="Senior Python Backend Engineer",
            company_name="TechCorp",
            must_have_skills=["Python", "FastAPI"],
            raw_text=raw_text,
        )


class MockATSMatcher(ATSMatcher):
    async def match(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        return JDMatchReport(
            overall_score=92,
            skill_match_score=95,
            experience_fit_score=90,
            format_quality_score=90,
            matched_skills=[
                SkillMatchItem(
                    skill_name="Python",
                    match_type="exact",
                    cv_evidence="Python",
                    jd_requirement="Python",
                    importance="required",
                )
            ],
            missing_skills=[],
            excess_skills=[],
            top_recommendations=["Tốt"],
            experience_gap_analysis="Phù hợp",
            jd_title=jd.job_title,
        )


from ai.models.critic import ReflectiveSynthesisResult, CriticEvaluationReport


class MockHarvardSynthesizer:
    async def synthesize(
        self, profile: CandidateProfile, jd: JDProfile, report: JDMatchReport, target_language: str = "vi"
    ) -> tuple[HarvardCVData, ReflectiveSynthesisResult]:
        cv = HarvardCVData(
            target_language=target_language,
            target_role=jd.job_title,
            company_name=jd.company_name,
            contact=HarvardContactInfo(
                full_name=profile.personal_info.full_name,
                email=profile.personal_info.email,
                phone=profile.personal_info.phone,
                location=profile.personal_info.location,
            ),
            summary=f"Kỹ sư phần mềm {jd.job_title} với nhiều năm kinh nghiệm.",
            education=[
                HarvardEducationItem(
                    institution="ĐH Bách Khoa",
                    degree_major="Kỹ sư CNTT",
                    graduation_year="2022",
                )
            ],
            experience=[
                HarvardExperienceItem(
                    company="VNG",
                    role="Backend Engineer",
                    date_range="2022 - Nay",
                    bullets=["Kiến trúc hệ thống FastAPI xử lý 30,000 req/s."],
                )
            ],
            projects=[
                HarvardProjectItem(
                    name="AI Agent",
                    role_or_tech="Lead",
                    bullets=["Phát triển engine tổng hợp CV."],
                )
            ],
            skills_categories=[
                HarvardSkillsCategory(
                    category_name="Languages & Frameworks",
                    skills=["Python", "FastAPI", "Docker"],
                )
            ],
            certifications_and_languages=HarvardCertAndLangSection(
                certifications=["AWS Architect"],
                languages=["English (Fluent)"],
            ),
            ats_score_estimate=92,
            estimated_word_count=380,
        )
        reflection = ReflectiveSynthesisResult(
            is_converged=True,
            iterations_count=1,
            final_critic_score=92,
            critic_report=CriticEvaluationReport(
                total_score=92,
                is_approved=True,
                dimension_scores={
                    "quantifiable_metrics": 25,
                    "anti_hallucination": 25,
                    "ats_alignment": 22,
                    "action_verbs_brevity": 20,
                },
            ),
            reflection_history=[],
        )
        return cv, reflection


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    upload_rate_limiter.reset()
    read_rate_limiter.reset()
    ats_rate_limiter.reset()
    star_rate_limiter.reset()
    cv_generation_rate_limiter.reset()
    yield
    upload_rate_limiter.reset()
    read_rate_limiter.reset()
    ats_rate_limiter.reset()
    star_rate_limiter.reset()
    cv_generation_rate_limiter.reset()


@pytest.fixture
def client():
    app.dependency_overrides[get_cached_jd_parser] = lambda: MockJDParser()
    app.dependency_overrides[get_cached_ats_matcher] = lambda: MockATSMatcher()
    app.dependency_overrides[get_cached_harvard_synthesizer] = lambda: MockHarvardSynthesizer()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    get_cached_jd_parser.cache_clear()
    get_cached_ats_matcher.cache_clear()
    get_cached_harvard_synthesizer.cache_clear()


@pytest_asyncio.fixture
async def sample_candidate_id():
    profile = CandidateProfile(
        personal_info=PersonalInfo(
            full_name="Nguyễn Văn C",
            email="c.nguyen@example.com",
            phone="0987654321",
            location="TP. Hồ Chí Minh",
        ),
        summary=SummarySection(detected_title="Senior Python Engineer"),
        education=[EducationItem(institution="ĐH Bách Khoa", degree="Kỹ sư", field_of_study="CNTT")],
        work_experience=[WorkExperienceItem(company="TechCorp", role="Backend Dev", start_date="2021", is_current=True)],
        skills_taxonomy=SkillsTaxonomy(programming_languages=["Python", "Go"]),
    )
    cid = await save_candidate(
        profile_json=profile.model_dump_json(),
        full_name="Nguyễn Văn C",
        email="c.nguyen@example.com",
        title="Senior Python Engineer",
    )
    return cid


@pytest.mark.asyncio
async def test_generate_cv_success(client, sample_candidate_id):
    cid = sample_candidate_id
    payload = {
        "candidate_id": cid,
        "jd_text": "Tuyển dụng Senior Python Backend Engineer với kinh nghiệm FastAPI, Docker, PostgreSQL...",
        "language": "vi",
        "format": "pdf",
    }
    response = client.post("/api/v1/ats/generate-cv", json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "Harvard_CV" in response.headers["Content-Disposition"]
    assert response.content.startswith(b"%PDF")
    assert int(response.headers["X-Estimated-ATS-Score"]) >= 80


@pytest.mark.asyncio
async def test_generate_cv_english(client, sample_candidate_id):
    cid = sample_candidate_id
    payload = {
        "candidate_id": cid,
        "jd_text": "Looking for a Senior Python Engineer with FastAPI and Docker experience...",
        "language": "en",
        "format": "pdf",
    }
    response = client.post("/api/v1/ats/generate-cv", json=payload)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert "_en.pdf" in response.headers["Content-Disposition"]
    assert response.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_cv_candidate_not_found(client):
    payload = {
        "candidate_id": "018db000-0000-7000-8000-000000000000",
        "jd_text": "Tuyển dụng Senior Python Backend Engineer...",
        "language": "vi",
        "format": "pdf",
    }
    response = client.post("/api/v1/ats/generate-cv", json=payload)
    assert response.status_code == 404
    assert "Không tìm thấy hồ sơ ứng viên" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_cv_jd_too_short(client, sample_candidate_id):
    cid = sample_candidate_id
    payload = {
        "candidate_id": cid,
        "jd_text": "Quá ngắn",
        "language": "vi",
        "format": "pdf",
    }
    response = client.post("/api/v1/ats/generate-cv", json=payload)
    # Validation error for length < 15
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_cv_rate_limiting(client, sample_candidate_id):
    cid = sample_candidate_id
    payload = {
        "candidate_id": cid,
        "jd_text": "Tuyển dụng Senior Python Backend Engineer với kinh nghiệm thực tế...",
        "language": "vi",
        "format": "pdf",
    }
    # Free tier: 5 requests max
    for _ in range(5):
        res = client.post("/api/v1/ats/generate-cv", json=payload)
        assert res.status_code == 200

    # 6th request should hit 429 Too Many Requests
    res6 = client.post("/api/v1/ats/generate-cv", json=payload)
    assert res6.status_code == 429
    assert "5 lần" in res6.json()["detail"]


@pytest.mark.asyncio
async def test_generate_cv_invalid_language(client, sample_candidate_id):
    cid = sample_candidate_id
    payload = {
        "candidate_id": cid,
        "jd_text": "Tuyển dụng Senior Python Backend Engineer với kinh nghiệm thực tế...",
        "language": "fr",  # Invalid, only 'vi' and 'en' allowed
        "format": "pdf",
    }
    res = client.post("/api/v1/ats/generate-cv", json=payload)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_generate_cv_invalid_format(client, sample_candidate_id):
    cid = sample_candidate_id
    payload = {
        "candidate_id": cid,
        "jd_text": "Tuyển dụng Senior Python Backend Engineer với kinh nghiệm thực tế...",
        "language": "vi",
        "format": "docx",  # Invalid, only 'pdf' allowed
    }
    res = client.post("/api/v1/ats/generate-cv", json=payload)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_rate_limiter_spoofed_header_blocked():
    """Test that direct untrusted clients cannot bypass limits using fake X-Forwarded-For."""
    from fastapi import HTTPException
    from be.core.rate_limiter import SlidingWindowRateLimiter

    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60, trusted_proxies={"127.0.0.1"})

    class UntrustedClientRequest:
        def __init__(self, spoofed_forwarded_ip: str):
            self.headers = {"X-Forwarded-For": spoofed_forwarded_ip}
            # Direct client connection from an untrusted peer IP
            self.client = type("Client", (), {"host": "198.51.100.50"})()
            self.url = type("URL", (), {"path": "/api/v1/test"})()

    # Attacker tries to bypass with different X-Forwarded-For headers
    await limiter(UntrustedClientRequest("1.1.1.1"))
    await limiter(UntrustedClientRequest("2.2.2.2"))

    # 3rd request from attacker should be rejected with 429 despite new spoofed header
    with pytest.raises(HTTPException) as exc_info:
        await limiter(UntrustedClientRequest("3.3.3.3"))
    assert exc_info.value.status_code == 429

