"""Unit tests for CandidateProfile (v3) canonical schema."""

import pytest
from ai.models.candidate import (
    CandidateProfile,
    PersonalInfo,
    SummarySection,
    WorkExperienceItem,
    EducationItem,
    ProjectItem,
    SkillsTaxonomy,
    CertificationItem,
    LanguageItem,
    AdditionalSectionItem,
    CVMetadata,
)


def test_candidate_profile_full_instantiation():
    profile = CandidateProfile(
        personal_info=PersonalInfo(
            full_name="Nguyễn Văn An",
            email="an.nguyen@example.com",
            phone="0901234567",
            location="Hồ Chí Minh",
            linkedin_url="https://linkedin.com/in/annguyen",
            github_url="https://github.com/annguyen",
            date_of_birth="1998-05-15",
        ),
        summary=SummarySection(
            summary_text="3+ năm kinh nghiệm phát triển AI & Backend systems.",
            detected_title="Senior AI Engineer",
        ),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python", "Go", "TypeScript"],
            frameworks=["FastAPI", "React", "PyTorch"],
            databases=["PostgreSQL", "Redis", "Qdrant"],
            devops_and_cloud=["Docker", "Kubernetes", "AWS"],
            ai_and_ml=["RAG", "LLMs", "Vector Search"],
            testing=["pytest", "Playwright"],
            tools=["Git", "Linux", "VS Code"],
            soft_skills=["Leadership", "Problem Solving"],
        ),
        work_experience=[
            WorkExperienceItem(
                company="VNG Corp",
                role="AI Engineer",
                start_date="2023-01",
                end_date=None,
                is_current=True,
                location="TP.HCM",
                raw_bullets=[
                    "Xây dựng hệ thống Enterprise RAG cho 20,000 nhân sự",
                    "Giảm latency truy vấn từ 1.2s xuống 280ms với Qdrant",
                ],
            )
        ],
        education=[
            EducationItem(
                institution="ĐH Bách Khoa TP.HCM",
                degree="Kỹ sư",
                field_of_study="Khoa học Máy tính",
                start_year=2016,
                end_year=2021,
                gpa="3.6/4.0",
            )
        ],
        projects=[
            ProjectItem(
                name="AI Career Agent",
                description="Hệ thống tự động hóa tìm việc",
                technologies=["FastAPI", "React", "Gemini"],
                url="https://github.com/example/career-agent",
            )
        ],
        certifications=[
            CertificationItem(
                name="AWS Solutions Architect Associate",
                issuer="AWS",
                issue_date="2023-08",
            )
        ],
        languages=[
            LanguageItem(language="Vietnamese", proficiency="Native"),
            LanguageItem(language="English", proficiency="IELTS 7.5"),
        ],
        additional_sections=[
            AdditionalSectionItem(
                section_name="Awards",
                section_type="awards",
                items=["Giải Nhất Hackathon 2023"],
            )
        ],
        metadata=CVMetadata(
            total_experience_years=3.8,
            cv_language="vi",
            extraction_confidence=98,
        ),
    )

    # Validate properties
    assert profile.full_name == "Nguyễn Văn An"
    assert profile.email == "an.nguyen@example.com"
    assert profile.title == "Senior AI Engineer"
    # math.floor(3.8) -> 3 years (conservative, non-inflated)
    assert profile.experience_years == 3
    assert len(profile.skills_taxonomy.programming_languages) == 3
    assert len(profile.work_experience[0].raw_bullets) == 2
    assert profile.languages[1].proficiency == "IELTS 7.5"
    assert profile.additional_sections[0].section_type == "awards"


def test_candidate_profile_minimal_defaults():
    profile = CandidateProfile(
        personal_info=PersonalInfo(full_name="Trần Thị B")
    )
    assert profile.full_name == "Trần Thị B"
    assert profile.email is None
    assert profile.title == ""
    assert profile.skills_taxonomy.programming_languages == []
    assert profile.work_experience == []
    assert profile.experience_years == 0
