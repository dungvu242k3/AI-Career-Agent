"""Unit tests for ATSMatcher (Scoring normalization, 50/30/20 weighting, grade mapping, and fallback)."""

import pytest
from unittest.mock import AsyncMock
from ai.analysis.ats_matcher import ATSMatcher
from ai.models.candidate import (
    CandidateProfile,
    PersonalInfo,
    SummarySection,
    SkillsTaxonomy,
    WorkExperienceItem,
)
from ai.models.jd import JDProfile, JDMatchReport, SkillMatchItem


@pytest.fixture
def sample_profile():
    return CandidateProfile(
        personal_info=PersonalInfo(full_name="Nguyễn Văn An", email="an@example.com"),
        summary=SummarySection(detected_title="Senior Python Backend Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python", "Go"],
            frameworks=["FastAPI", "Django"],
            databases=["PostgreSQL", "Redis"],
            devops_and_cloud=["Docker", "AWS"],
        ),
        work_experience=[
            WorkExperienceItem(
                company="VNG",
                role="Senior Backend Engineer",
                start_date="2021-01",
                raw_bullets=[
                    "Thiết kế hệ thống microservices xử lý 25,000 req/s, giảm 40% latency.",
                    "Triển khai Redis Caching tăng tốc độ truy vấn API lên 5 lần.",
                ],
            )
        ],
    )


@pytest.fixture
def sample_jd():
    return JDProfile(
        job_title="Senior Backend Engineer",
        company_name="Shopee",
        must_have_skills=["Python", "FastAPI", "PostgreSQL"],
        nice_to_have_skills=["Redis", "Kubernetes"],
        min_experience_years=3,
        responsibilities=["Xây dựng hệ thống backend hiệu năng cao", "Tối ưu hóa cơ sở dữ liệu"],
        raw_text="Shopee tuyển Senior Backend Engineer Python FastAPI PostgreSQL",
    )


@pytest.fixture
def sample_report():
    return JDMatchReport(
        overall_score=85,
        skill_match_score=90,
        experience_fit_score=80,
        format_quality_score=75,
        matched_skills=[
            SkillMatchItem(
                skill_name="Python",
                match_type="exact",
                cv_evidence="Python listed",
                jd_requirement="Python required",
                importance="required",
            ),
            SkillMatchItem(
                skill_name="FastAPI",
                match_type="exact",
                cv_evidence="FastAPI listed",
                jd_requirement="FastAPI required",
                importance="required",
            ),
        ],
        missing_skills=[
            SkillMatchItem(
                skill_name="Kubernetes",
                match_type="missing",
                cv_evidence=None,
                jd_requirement="Kubernetes preferred",
                importance="preferred",
            )
        ],
        top_recommendations=[
            "Bổ sung dự án thực tế về Kubernetes",
            "Thêm chứng chỉ AWS Certified Solutions Architect",
            "Làm rõ số liệu cho dự án tại VNG",
        ],
        experience_gap_analysis="Ứng viên đáp ứng tốt 90% kỹ năng cốt lõi cho vị trí Senior Backend.",
        jd_title="Senior Backend Engineer",
    )


def test_normalize_report_weights(sample_report, sample_jd):
    matcher = ATSMatcher()
    # Skills = 90 (50%), Exp = 80 (30%), Format = 70 (20%) -> 45 + 24 + 14 = 83
    sample_report.skill_match_score = 90
    sample_report.experience_fit_score = 80
    sample_report.format_quality_score = 70
    sample_report.overall_score = 0  # Should be recalculated

    normalized = matcher._normalize_report(sample_report, sample_jd)
    assert normalized.overall_score == 83
    assert normalized.overall_grade == "A"
    assert "Phù hợp tốt" in normalized.verdict


def test_grade_and_verdict_mapping(sample_report, sample_jd):
    matcher = ATSMatcher()

    # Test A+ (>= 90)
    sample_report.skill_match_score = 95
    sample_report.experience_fit_score = 95
    sample_report.format_quality_score = 95
    res = matcher._normalize_report(sample_report, sample_jd)
    assert res.overall_grade == "A+"
    assert "Rất phù hợp" in res.verdict

    # Test B (60-69)
    sample_report.skill_match_score = 65
    sample_report.experience_fit_score = 65
    sample_report.format_quality_score = 65
    res = matcher._normalize_report(sample_report, sample_jd)
    assert res.overall_grade == "B"

    # Test C (<60)
    sample_report.skill_match_score = 40
    sample_report.experience_fit_score = 40
    sample_report.format_quality_score = 40
    res = matcher._normalize_report(sample_report, sample_jd)
    assert res.overall_grade == "C"
    assert "Chưa phù hợp" in res.verdict


@pytest.mark.asyncio
async def test_ats_matcher_openai_success(sample_profile, sample_jd, sample_report):
    matcher = ATSMatcher(ai_provider="openai")
    matcher._match_with_openai = AsyncMock(return_value=sample_report)

    result = await matcher.match(sample_profile, sample_jd)
    assert result.overall_score == 85
    assert len(result.matched_skills) == 2
    assert len(result.missing_skills) == 1
    assert matcher._match_with_openai.called


@pytest.mark.asyncio
async def test_ats_matcher_fallback_on_primary_error(sample_profile, sample_jd, sample_report):
    matcher = ATSMatcher(ai_provider="openai", enable_fallback=True)
    matcher._match_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI 500 error"))
    matcher._match_with_gemini = AsyncMock(return_value=sample_report)

    result = await matcher.match(sample_profile, sample_jd)
    assert result.overall_score == 85
    assert matcher._match_with_openai.called
    assert matcher._match_with_gemini.called


@pytest.mark.asyncio
async def test_ats_matcher_raises_when_both_fail(sample_profile, sample_jd):
    matcher = ATSMatcher(ai_provider="openai", enable_fallback=True)
    matcher._match_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI failed"))
    matcher._match_with_gemini = AsyncMock(side_effect=RuntimeError("Gemini failed"))

    with pytest.raises(ValueError) as exc:
        await matcher.match(sample_profile, sample_jd)
    assert "thất bại trên cả 2 nhà cung cấp" in str(exc.value)


def test_contextual_proof_calculation(sample_report, sample_jd, sample_profile):
    matcher = ATSMatcher()
    
    # 2 out of 2 matched skills are proven (100% verified)
    sample_report.matched_skills[0].has_contextual_proof = True
    sample_report.matched_skills[1].has_contextual_proof = True
    normalized = matcher._normalize_report(sample_report, sample_jd, profile=sample_profile)
    assert normalized.verified_skills_ratio == 1.0
    assert normalized.skill_density_status == "optimal"

    # Only 1 out of 4 is proven (25% verified < 60% threshold -> penalty applied)
    sample_report.matched_skills = [
        SkillMatchItem(skill_name="Python", match_type="exact", jd_requirement="req", importance="required", has_contextual_proof=True),
        SkillMatchItem(skill_name="FastAPI", match_type="exact", jd_requirement="req", importance="required", has_contextual_proof=False),
        SkillMatchItem(skill_name="PostgreSQL", match_type="exact", jd_requirement="req", importance="required", has_contextual_proof=False),
        SkillMatchItem(skill_name="Docker", match_type="exact", jd_requirement="req", importance="required", has_contextual_proof=False),
    ]
    sample_report.skill_match_score = 100
    normalized_penalized = matcher._normalize_report(sample_report, sample_jd, profile=sample_profile)
    assert normalized_penalized.verified_skills_ratio == 0.25
    # penalty factor = 0.70 + 0.30 * 0.25 = 0.775 -> 100 * 0.775 = 77 or 78 depending on float precision
    assert normalized_penalized.skill_match_score in (77, 78)


def test_skill_density_bloating_penalty(sample_report, sample_jd):
    matcher = ATSMatcher()

    # Create bloated profile with 30 skills (>25 threshold)
    bloated_profile = CandidateProfile(
        personal_info=PersonalInfo(full_name="Nguyễn Văn B", email="b@example.com"),
        summary=SummarySection(detected_title="Backend Developer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python", "Go", "Java", "C++", "Rust", "PHP", "Ruby", "C#"],
            frameworks=["FastAPI", "Django", "Flask", "Spring", "Laravel", "Rails", "Express", "NestJS"],
            databases=["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Neo4j"],
            devops_and_cloud=["Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Ansible", "Jenkins"],
        ),
        work_experience=[],
    )

    sample_report.format_quality_score = 80
    normalized = matcher._normalize_report(sample_report, sample_jd, profile=bloated_profile)
    
    assert normalized.total_cv_skills_count == 31
    assert normalized.skill_density_status == "bloated"
    # Format score reduced by 10 points for bloated keyword stuffing (80 - 10 = 70)
    assert normalized.format_quality_score == 70
    assert len(normalized.pruning_suggestions) > 0
    assert "tinh gọn" in normalized.pruning_suggestions[0]

