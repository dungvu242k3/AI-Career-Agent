"""Unit tests for Harvard PDF Rendering Engine (be/core/cv_renderer.py)."""

import pytest
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardContactInfo,
    HarvardEducationItem,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
    HarvardCertAndLangSection,
)
from be.core.cv_renderer import HarvardPDFRenderer


@pytest.fixture
def sample_harvard_cv_data():
    return HarvardCVData(
        target_language="vi",
        target_role="Senior AI Engineer",
        company_name="VNG Corporation",
        contact=HarvardContactInfo(
            full_name="Nguyễn Văn A",
            email="nguyenvana@example.com",
            phone="0912345678",
            location="Hà Nội, Việt Nam",
            linkedin_url="https://linkedin.com/in/nguyenvana",
            github_url="https://github.com/nguyenvana",
        ),
        summary="Kỹ sư AI và Backend với 4+ năm kinh nghiệm phát triển hệ thống LLM phục vụ hơn 50,000 người dùng hàng ngày.",
        education=[
            HarvardEducationItem(
                institution="Đại học Bách Khoa Hà Nội",
                degree_major="Kỹ sư Công nghệ Thông tin",
                graduation_year="2018 - 2022",
                gpa_honors="GPA: 3.65/4.0",
            )
        ],
        experience=[
            HarvardExperienceItem(
                company="Tập đoàn Công nghệ FPT",
                role="Senior Backend Engineer",
                date_range="06/2022 - Hiện tại",
                location="Hà Nội",
                bullets=[
                    "Kiến trúc hệ thống microservices xử lý 25,000 req/s, giảm 40% độ trễ API.",
                    "Triển khai pipeline CI/CD tự động hóa trên Kubernetes, tăng 3x tốc độ release.",
                ],
            )
        ],
        projects=[
            HarvardProjectItem(
                name="AI Career Agent",
                role_or_tech="Lead Architect | FastAPI, PyTorch, Docker",
                date_range="2024",
                bullets=[
                    "Xây dựng engine phân tích ATS 3 trụ cột và sinh CV theo chuẩn Harvard 1 trang.",
                ],
            )
        ],
        skills_categories=[
            HarvardSkillsCategory(
                category_name="Ngôn ngữ & Frameworks",
                skills=["Python", "FastAPI", "Go", "React", "PyTorch"],
            ),
            HarvardSkillsCategory(
                category_name="Hạ tầng & Dữ liệu",
                skills=["Docker", "Kubernetes", "PostgreSQL", "Redis", "AWS"],
            ),
        ],
        certifications_and_languages=HarvardCertAndLangSection(
            certifications=["AWS Certified Solutions Architect", "CKA Kubernetes"],
            languages=["Tiếng Việt (Bản ngữ)", "Tiếng Anh (IELTS 7.5)"],
        ),
        ats_score_estimate=94,
    )


def test_render_pdf_returns_valid_bytes(sample_harvard_cv_data):
    pdf_bytes = HarvardPDFRenderer.render(sample_harvard_cv_data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF magic bytes check
    assert pdf_bytes.startswith(b"%PDF")


def test_render_english_cv(sample_harvard_cv_data):
    sample_harvard_cv_data.target_language = "en"
    sample_harvard_cv_data.summary = "Senior AI Engineer with 4+ years of production experience."
    pdf_bytes = HarvardPDFRenderer.render(sample_harvard_cv_data)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")


def test_render_minimal_cv():
    minimal_cv = HarvardCVData(
        target_language="vi",
        target_role="Software Engineer",
        contact=HarvardContactInfo(full_name="Trần Thị B"),
    )
    pdf_bytes = HarvardPDFRenderer.render(minimal_cv)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
