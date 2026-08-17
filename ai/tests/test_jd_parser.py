"""Unit tests for JDParser (In-memory file/text extraction, validation, auto-healing, and multi-provider fallback)."""

import pytest
from unittest.mock import AsyncMock, patch
from ai.models.jd import JDProfile
from ai.parsers.jd_parser import (
    JDParser,
    MAX_JD_TEXT_LENGTH,
    MAX_JD_FILE_SIZE_BYTES,
)


@pytest.fixture
def sample_jd_profile():
    return JDProfile(
        job_title="Senior Python Backend Engineer",
        company_name="TechCorp Vietnam",
        must_have_skills=["Python", "FastAPI", "PostgreSQL"],
        nice_to_have_skills=["Redis", "Docker", "Kubernetes"],
        min_experience_years=3,
        education_requirement="Bachelor in Computer Science or related",
        responsibilities=["Develop scalable microservices", "Optimize database queries"],
        benefits=["13th month salary", "Hybrid work mode"],
        raw_text="Sample JD raw text",
        language="vi",
    )


@pytest.mark.asyncio
async def test_parse_jd_text_validation_empty():
    parser = JDParser()
    with pytest.raises(ValueError) as exc:
        await parser.parse_jd_text("")
    assert "không được để trống" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        await parser.parse_jd_text("   short   ")
    assert "không được để trống" in str(exc.value)


def test_sanitize_text_truncation():
    parser = JDParser()
    long_text = "A" * (MAX_JD_TEXT_LENGTH + 500)
    cleaned = parser._sanitize_text(long_text)
    assert len(cleaned) == MAX_JD_TEXT_LENGTH


@pytest.mark.asyncio
async def test_parse_jd_file_validation():
    parser = JDParser()

    # Unsupported extension
    with pytest.raises(ValueError) as exc:
        await parser.parse_jd_file(b"test content", filename="job.txt")
    assert "Chỉ chấp nhận tệp định dạng PDF" in str(exc.value)

    # Empty bytes
    with pytest.raises(ValueError) as exc:
        await parser.parse_jd_file(b"", filename="job.pdf")
    assert "rỗng hoặc bị lỗi" in str(exc.value)

    # Oversized file (>2MB)
    oversized = b"0" * (MAX_JD_FILE_SIZE_BYTES + 1024)
    with pytest.raises(ValueError) as exc:
        await parser.parse_jd_file(oversized, filename="job.pdf")
    assert "vượt quá giới hạn cho phép (2MB)" in str(exc.value)


def test_auto_heal_jd(sample_jd_profile):
    parser = JDParser()
    sample_jd_profile.must_have_skills = ["Python", "python", "FASTAPI", "FastAPI"]
    healed = parser._auto_heal_jd(sample_jd_profile, "New raw text")

    assert len(healed.must_have_skills) == 2
    assert "Python" in healed.must_have_skills
    assert "FASTAPI" in healed.must_have_skills
    assert healed.raw_text == "New raw text"


@pytest.mark.asyncio
async def test_parse_jd_text_openai_success(sample_jd_profile):
    parser = JDParser(ai_provider="openai")
    parser._extract_with_openai = AsyncMock(return_value=sample_jd_profile)

    result = await parser.parse_jd_text("Senior Backend Engineer JD with Python and FastAPI")
    assert result.job_title == "Senior Python Backend Engineer"
    assert "Python" in result.must_have_skills
    assert parser._extract_with_openai.called


@pytest.mark.asyncio
async def test_parse_jd_text_auto_fallback_on_primary_error(sample_jd_profile):
    parser = JDParser(ai_provider="openai", enable_fallback=True)
    parser._extract_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI API rate limit 429"))
    parser._extract_with_gemini = AsyncMock(return_value=sample_jd_profile)

    result = await parser.parse_jd_text("Senior Backend Engineer JD with Python and FastAPI")
    assert result.job_title == "Senior Python Backend Engineer"
    assert parser._extract_with_openai.called
    assert parser._extract_with_gemini.called


@pytest.mark.asyncio
async def test_parse_jd_text_raises_when_both_fail():
    parser = JDParser(ai_provider="openai", enable_fallback=True)
    parser._extract_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI failed"))
    parser._extract_with_gemini = AsyncMock(side_effect=RuntimeError("Gemini failed"))

    with pytest.raises(ValueError) as exc:
        await parser.parse_jd_text("Senior Backend Engineer JD with Python and FastAPI")
    assert "thất bại trên cả 2 nhà cung cấp" in str(exc.value)


@pytest.mark.asyncio
async def test_parse_jd_file_pdf_flow(sample_jd_profile):
    parser = JDParser(ai_provider="openai")
    parser.pdf_parser.extract_text_from_bytes = lambda b, filename: "Extracted PDF text for Senior Python"
    parser._extract_with_openai = AsyncMock(return_value=sample_jd_profile)

    result = await parser.parse_jd_file(b"%PDF-1.4 dummy pdf bytes", filename="job_desc.pdf")
    assert result.job_title == "Senior Python Backend Engineer"


@pytest.mark.asyncio
async def test_parse_jd_file_docx_flow(sample_jd_profile):
    parser = JDParser(ai_provider="openai")
    parser.docx_parser.extract_text_from_bytes = lambda b, filename: "Extracted DOCX text for Senior Python"
    parser._extract_with_openai = AsyncMock(return_value=sample_jd_profile)

    result = await parser.parse_jd_file(b"\x50\x4B\x03\x04 dummy docx bytes", filename="job_desc.docx")
    assert result.job_title == "Senior Python Backend Engineer"
