"""Unit tests for Harvard 1-Page CV Synthesizer engine."""

import pytest
from unittest.mock import AsyncMock

from ai.analysis.harvard_synthesizer import HarvardCVSynthesizer
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, EducationItem, WorkExperienceItem, ProjectItem, SkillsTaxonomy
from ai.models.jd import JDProfile, JDMatchReport, SkillMatchItem
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardContactInfo,
    HarvardEducationItem,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
    HarvardCertAndLangSection,
)


@pytest.fixture
def sample_candidate_profile():
    return CandidateProfile(
        personal_info=PersonalInfo(
            full_name="Nguyễn Văn A",
            email="nguyenvana@gmail.com",
            phone="0912345678",
            location="Hà Nội, Việt Nam",
            linkedin_url="https://linkedin.com/in/nguyenvana",
            github_url="https://github.com/nguyenvana",
        ),
        summary=SummarySection(
            summary_text="Kỹ sư phần mềm 4 năm kinh nghiệm chuyên sâu về FastAPI, Docker, Microservices.",
            detected_title="Senior Backend Engineer",
        ),
        education=[
            EducationItem(
                institution="Đại học Bách Khoa Hà Nội",
                degree="Kỹ sư",
                field_of_study="Công nghệ Thông tin",
                start_year=2018,
                end_year=2022,
                gpa="3.6/4.0",
            )
        ],
        work_experience=[
            WorkExperienceItem(
                company="Công ty Cổ phần VNG",
                role="Backend Engineer",
                start_date="2022-06",
                end_date=None,
                is_current=True,
                location="Hà Nội",
                raw_bullets=[
                    "Xây dựng hệ thống thanh toán điện tử bằng FastAPI và Redis.",
                    "Tối ưu hóa truy vấn PostgreSQL, giảm 45% thời gian phản hồi.",
                ],
            )
        ],
        projects=[
            ProjectItem(
                name="AI Career Agent",
                description="Hệ thống tối ưu hồ sơ CV và luyện phỏng vấn thông minh.",
                role="Lead Developer",
                technologies=["Python", "FastAPI", "React", "Docker"],
                highlights=["Phục vụ 5,000+ người dùng hoạt động hàng tháng."],
            )
        ],
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python", "Go", "SQL"],
            frameworks=["FastAPI", "Django", "React"],
            databases=["PostgreSQL", "Redis", "MongoDB"],
            devops_and_cloud=["Docker", "Kubernetes", "AWS", "CI/CD"],
            tools=["Git", "Linux"],
        ),
    )


@pytest.fixture
def sample_jd_profile():
    return JDProfile(
        job_title="Senior Python Backend Engineer",
        company_name="TechCorp Vietnam",
        must_have_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        nice_to_have_skills=["Kubernetes", "AWS"],
        min_experience_years=3,
        responsibilities=["Thiết kế kiến trúc hệ thống backend microservices."],
        raw_text="Tuyển dụng Senior Python Backend Engineer tại TechCorp Vietnam...",
        language="vi",
    )


@pytest.fixture
def sample_match_report():
    return JDMatchReport(
        overall_score=88,
        overall_grade="A",
        verdict="Rất phù hợp",
        skill_match_score=90,
        experience_fit_score=85,
        format_quality_score=90,
        matched_skills=[
            SkillMatchItem(
                skill_name="Python",
                match_type="exact",
                cv_evidence="Python",
                jd_requirement="Python",
                importance="required",
            ),
            SkillMatchItem(
                skill_name="FastAPI",
                match_type="exact",
                cv_evidence="FastAPI",
                jd_requirement="FastAPI",
                importance="required",
            ),
            SkillMatchItem(
                skill_name="PostgreSQL",
                match_type="exact",
                cv_evidence="PostgreSQL",
                jd_requirement="PostgreSQL",
                importance="required",
            ),
        ],
        missing_skills=[],
        excess_skills=["Go", "MongoDB"],
        top_recommendations=["Nhấn mạnh các dự án tối ưu hiệu năng"],
        experience_gap_analysis="Kinh nghiệm 4 năm vượt mức tối thiểu 3 năm.",
        jd_title="Senior Python Backend Engineer",
        analysis_language="vi",
    )


def test_prepare_payload(sample_candidate_profile, sample_jd_profile, sample_match_report):
    synthesizer = HarvardCVSynthesizer()
    payload = synthesizer._prepare_payload(
        sample_candidate_profile, sample_jd_profile, sample_match_report, "vi"
    )
    assert "<target_language>vi</target_language>" in payload
    assert "<candidate_profile>" in payload
    assert "<job_description>" in payload
    assert "<ats_match_report>" in payload


def test_post_process_skills_capping(sample_candidate_profile):
    synthesizer = HarvardCVSynthesizer()
    # Create CV with 25 skills
    bloated_skills = [
        HarvardSkillsCategory(
            category_name="Cat1",
            skills=[f"Skill_{i}" for i in range(15)],
        ),
        HarvardSkillsCategory(
            category_name="Cat2",
            skills=[f"Skill_Extra_{i}" for i in range(10)],
        ),
    ]
    cv = HarvardCVData(
        target_language="vi",
        target_role="Senior Engineer",
        contact=HarvardContactInfo(full_name="Nguyễn Văn A"),
        skills_categories=bloated_skills,
    )
    processed = synthesizer._post_process_cv(cv, sample_candidate_profile)
    total_skills = sum(len(c.skills) for c in processed.skills_categories)
    assert total_skills <= 15
    assert processed.estimated_word_count > 0


def test_heuristic_fallback_bilingual(sample_candidate_profile, sample_jd_profile, sample_match_report):
    synthesizer = HarvardCVSynthesizer()

    # Test Vietnamese fallback
    cv_vi = synthesizer._synthesize_heuristic_fallback(
        sample_candidate_profile, sample_jd_profile, sample_match_report, "vi"
    )
    assert cv_vi.target_language == "vi"
    assert cv_vi.contact.full_name == "Nguyễn Văn A"
    assert "Kỹ sư" in cv_vi.summary
    assert len(cv_vi.experience) > 0
    assert len(cv_vi.projects) > 0
    assert sum(len(c.skills) for c in cv_vi.skills_categories) <= 15

    # Test English fallback
    cv_en = synthesizer._synthesize_heuristic_fallback(
        sample_candidate_profile, sample_jd_profile, sample_match_report, "en"
    )
    assert cv_en.target_language == "en"
    assert "experience" in cv_en.summary.lower()


@pytest.mark.asyncio
async def test_synthesize_with_fallback(sample_candidate_profile, sample_jd_profile, sample_match_report):
    synthesizer = HarvardCVSynthesizer(ai_provider="openai", enable_fallback=True)
    # Mock primary and fallback providers to fail -> should trigger heuristic fallback safely
    synthesizer._synthesize_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI down"))
    synthesizer._synthesize_with_gemini = AsyncMock(side_effect=RuntimeError("Gemini down"))

    result = await synthesizer.synthesize(
        sample_candidate_profile, sample_jd_profile, sample_match_report, "vi"
    )
    assert result is not None
    assert result.contact.full_name == "Nguyễn Văn A"
    assert len(result.skills_categories) > 0
