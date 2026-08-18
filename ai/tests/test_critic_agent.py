"""Unit tests for Critic Agent 4-dimension audit."""

import pytest
from ai.analysis.critic_agent import CriticAgent
from ai.models.candidate import (
    CandidateProfile,
    PersonalInfo,
    SummarySection,
    SkillsTaxonomy,
    WorkExperienceItem,
    ProjectItem,
    CVMetadata,
)
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardContactInfo,
    HarvardEducationItem,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
)


@pytest.fixture
def sample_candidate_profile():
    return CandidateProfile(
        personal_info=PersonalInfo(
            full_name="Nguyễn Văn A",
            email="nguyenvana@gmail.com",
            phone="0901234567",
            location="Hà Nội",
        ),
        summary=SummarySection(
            summary_text="Senior Backend Engineer với 4 năm kinh nghiệm Python, FastAPI, PostgreSQL.",
            detected_title="Senior Backend Engineer",
        ),
        skills_taxonomy=SkillsTaxonomy(
            languages_and_frameworks=["Python", "FastAPI", "Django"],
            cloud_and_databases=["PostgreSQL", "Redis", "Docker"],
            specialized_engineering=["Microservices", "CI/CD"],
        ),
        work_experience=[
            WorkExperienceItem(
                company="Công ty Tech A",
                role="Senior Backend Developer",
                start_date="2022-01-01",
                end_date=None,
                is_current=True,
                raw_bullets=[
                    "Thiết kế kiến trúc microservices với FastAPI phục vụ 500k DAU.",
                    "Tối ưu hóa truy vấn PostgreSQL giảm 45% thời gian phản hồi API.",
                ],
            )
        ],
        projects=[
            ProjectItem(
                name="Hệ Thống Thanh Toán Realtime",
                description="Hệ thống xử lý giao dịch",
                technologies=["FastAPI", "Kafka", "PostgreSQL"],
            )
        ],
        metadata=CVMetadata(
            extraction_confidence=95,
            cv_language="vi",
            cv_format_type="chronological",
            total_experience_years=4.0,
        ),
    )


@pytest.fixture
def high_quality_cv_data():
    return HarvardCVData(
        target_language="vi",
        target_role="Senior Backend Engineer",
        contact=HarvardContactInfo(
            full_name="Nguyễn Văn A",
            email="nguyenvana@gmail.com",
            phone="0901234567",
            location="Hà Nội",
        ),
        summary="Senior Backend Engineer với 4+ năm kinh nghiệm kiến trúc hệ thống phân tán, xử lý 1M DAU.",
        education=[
            HarvardEducationItem(
                institution="Đại Học Bách Khoa Hà Nội",
                degree_major="Kỹ sư Công nghệ Thông tin",
                graduation_year="2018 - 2022",
                gpa_honors="GPA 3.6/4.0",
            )
        ],
        experience=[
            HarvardExperienceItem(
                company="Công ty Tech A",
                role="Senior Backend Developer",
                date_range="01/2022 - Hiện tại",
                location="Hà Nội",
                bullets=[
                    "Thiết kế kiến trúc Microservices FastAPI, xử lý 10,000 req/s với 99.9% uptime.",
                    "Tối ưu hóa PostgreSQL index và Redis cache, giảm 45% latency cho 500k DAU.",
                    "Tự động hóa CI/CD pipeline với GitHub Actions, rút ngắn 50% thời gian deploy.",
                ],
            )
        ],
        projects=[
            HarvardProjectItem(
                name="Realtime Payment Processing System",
                role_or_tech="Lead Backend | FastAPI, Kafka, Redis, PostgreSQL",
                date_range="2023",
                bullets=[
                    "Xây dựng event-driven architecture với Kafka, xử lý 2M giao dịch/ngày an toàn 100%.",
                ],
            )
        ],
        skills_categories=[
            HarvardSkillsCategory(
                category_name="Languages & Frameworks",
                skills=["Python", "FastAPI", "Django", "SQL"],
            ),
            HarvardSkillsCategory(
                category_name="Databases & Cloud",
                skills=["PostgreSQL", "Redis", "Docker", "Kafka", "AWS"],
            ),
            HarvardSkillsCategory(
                category_name="Architecture & Practices",
                skills=["Microservices", "CI/CD", "Event-Driven", "RESTful API"],
            ),
        ],
    )


def test_critic_high_quality_cv_approved(high_quality_cv_data, sample_candidate_profile):
    """Test that a well-quantified, action-verb grounded CV passes Critic Agent review."""
    critic = CriticAgent(approval_threshold=85)
    report = critic.evaluate(
        cv_data=high_quality_cv_data,
        raw_profile=sample_candidate_profile,
        iteration=1,
    )

    assert report.total_score >= 85
    assert report.is_approved is True
    assert report.dimension_scores["quantifiable_metrics"] >= 20
    assert report.dimension_scores["anti_hallucination"] >= 20
    assert len(report.flagged_hallucinations) == 0


def test_critic_flags_weak_bullets_and_hallucinations(sample_candidate_profile):
    """Test that passive voice and ungrounded tech stack get penalized by Critic."""
    weak_cv = HarvardCVData(
        target_language="vi",
        target_role="Rust & Blockchain Lead",
        contact=HarvardContactInfo(full_name="Nguyễn Văn A"),
        experience=[
            HarvardExperienceItem(
                company="Tech A",
                role="Developer",
                date_range="2022 - 2024",
                bullets=[
                    "Chịu trách nhiệm làm việc với backend và hỗ trợ các bạn trong nhóm.",
                    "Tham gia vào dự án và sửa một số lỗi.",
                ],
            )
        ],
        skills_categories=[
            HarvardSkillsCategory(
                category_name="Blockchain",
                skills=["Solidity", "Rust", "Ethereum", "Smart Contracts", "Web3"],
            )
        ],
    )

    critic = CriticAgent(approval_threshold=90)
    report = critic.evaluate(
        cv_data=weak_cv,
        raw_profile=sample_candidate_profile,
        target_jd_text="Cần 3 năm kinh nghiệm lập trình Solidity và Rust Smart Contracts",
    )

    assert report.total_score < 80
    assert report.is_approved is False
    assert len(report.critique_feedback) > 0
    assert len(report.actionable_improvements) > 0


def test_critic_handles_leading_bullet_symbols(sample_candidate_profile):
    """Test that bullets starting with '•' or '-' are correctly recognized for Harvard action verbs."""
    bullet_cv = HarvardCVData(
        target_language="vi",
        target_role="Senior Backend Engineer",
        contact=HarvardContactInfo(full_name="Nguyễn Văn A"),
        experience=[
            HarvardExperienceItem(
                company="Tech A",
                role="Senior Backend Developer",
                date_range="2022 - 2024",
                bullets=[
                    "• Thiết kế kiến trúc microservices giảm 35% latency API.",
                    "- Tối ưu hóa cơ sở dữ liệu PostgreSQL tăng 50% throughput.",
                    "• Spearheaded system migration to Kubernetes with 99.99% uptime.",
                ],
            )
        ],
        skills_categories=[
            HarvardSkillsCategory(
                category_name="Backend Core",
                skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "Kafka", "CI/CD", "Kubernetes"],
            )
        ],
    )

    critic = CriticAgent(approval_threshold=90)
    report = critic.evaluate(cv_data=bullet_cv, raw_profile=sample_candidate_profile)

    assert report.dimension_scores["action_verbs_brevity"] == 25
    assert report.dimension_scores["quantifiable_metrics"] == 25
