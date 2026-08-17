"""Unit tests for STARRewriter (Weak bullet point rewriting, missing skill generation, validation, and multi-provider fallback)."""

import pytest
from unittest.mock import AsyncMock
from ai.analysis.star_rewriter import STARRewriter
from ai.models.star import STARResult


@pytest.fixture
def sample_star_result():
    return STARResult(
        original="Làm backend bằng FastAPI",
        star_v1="Xây dựng hệ thống microservices bằng FastAPI phục vụ 30,000 req/s, giảm 40% độ trễ API.",
        star_v2="Kiến trúc hạ tầng phân tán hiệu năng cao với FastAPI và PostgreSQL, tối ưu 60% chi phí server.",
        action_verb="Kiến trúc",
        improvements=[
            "Thay thế động từ bị động 'Làm' bằng động từ hành động mạnh 'Kiến trúc/Xây dựng'",
            "Bổ sung số liệu lưu lượng truy cập cụ thể (30,000 req/s)",
            "Đo lường kết quả định lượng về độ trễ và chi phí hạ tầng",
        ],
    )


@pytest.mark.asyncio
async def test_rewrite_validation_empty_input():
    rewriter = STARRewriter()
    with pytest.raises(ValueError) as exc:
        await rewriter.rewrite("")
    assert "không được để trống" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        await rewriter.rewrite(" ")
    assert "không được để trống" in str(exc.value)


def test_prepare_payload_structure():
    rewriter = STARRewriter()
    payload = rewriter._prepare_payload("Redis", "Senior Backend Engineer", "VNG Cloud project")
    assert "<target_role>Senior Backend Engineer</target_role>" in payload
    assert "<raw_input>Redis</raw_input>" in payload
    assert "<additional_context>VNG Cloud project</additional_context>" in payload


@pytest.mark.asyncio
async def test_rewrite_openai_success(sample_star_result):
    rewriter = STARRewriter(ai_provider="openai")
    rewriter._rewrite_with_openai = AsyncMock(return_value=sample_star_result)

    result = await rewriter.rewrite("Làm backend bằng FastAPI", "Senior Backend Engineer")
    assert result.original == "Làm backend bằng FastAPI"
    assert "FastAPI" in result.star_v1
    assert result.action_verb == "Kiến trúc"
    assert len(result.improvements) == 3
    assert rewriter._rewrite_with_openai.called


@pytest.mark.asyncio
async def test_rewrite_fallback_on_primary_error(sample_star_result):
    rewriter = STARRewriter(ai_provider="openai", enable_fallback=True)
    rewriter._rewrite_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI 429 quota exceeded"))
    rewriter._rewrite_with_gemini = AsyncMock(return_value=sample_star_result)

    result = await rewriter.rewrite("Redis", "Lead Backend Engineer")
    assert result.original == "Redis"
    assert rewriter._rewrite_with_openai.called
    assert rewriter._rewrite_with_gemini.called


@pytest.mark.asyncio
async def test_rewrite_raises_when_both_fail():
    rewriter = STARRewriter(ai_provider="openai", enable_fallback=True)
    rewriter._rewrite_with_openai = AsyncMock(side_effect=RuntimeError("OpenAI error"))
    rewriter._rewrite_with_gemini = AsyncMock(side_effect=RuntimeError("Gemini error"))

    with pytest.raises(ValueError) as exc:
        await rewriter.rewrite("Kubernetes", "DevOps Engineer")
    assert "thất bại trên cả 2 nhà cung cấp" in str(exc.value)
