"""Unit tests for CVIngestionPipeline, auto-healing, and multi-provider fallback."""

import pytest
from unittest.mock import AsyncMock
from ai.pipeline import CVIngestionPipeline
from ai.interfaces.parser import BaseDocumentParser
from ai.interfaces.extractor import BaseProfileExtractor
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy


class MockParser(BaseDocumentParser):
    def extract_text_from_bytes(self, content_bytes: bytes, filename: str = "upload.pdf") -> str:
        return "Nguyen Van A\nPython Developer"

    def extract_text_from_file(self, file_path) -> str:
        return "Nguyen Van A\nPython Developer"


class MockSuccessfulExtractor(BaseProfileExtractor):
    def __init__(self, name: str = "Nguyen Van A"):
        self.name = name

    async def extract_profile(self, raw_text: str) -> CandidateProfile:
        return CandidateProfile(
            personal_info=PersonalInfo(full_name=self.name, email="an@test.com"),
            summary=SummarySection(detected_title="Python Developer"),
            skills_taxonomy=SkillsTaxonomy(programming_languages=["Python", "Go"]),
        )


class MockFailingExtractor(BaseProfileExtractor):
    async def extract_profile(self, raw_text: str) -> CandidateProfile:
        raise ValueError("Primary provider rate limit exceeded (429)")


@pytest.mark.asyncio
async def test_cv_ingestion_pipeline_primary_success():
    pipeline = CVIngestionPipeline(
        parser=MockParser(),
        primary_extractor=MockSuccessfulExtractor(name="Primary Extractor Result"),
        fallback_extractor=MockSuccessfulExtractor(name="Fallback Extractor Result"),
        enable_fallback=True,
    )

    raw_text, profile = await pipeline.process_bytes(b"%PDF-1.4 sample bytes")

    assert "Nguyen Van A" in raw_text
    assert profile.full_name == "Primary Extractor Result"


@pytest.mark.asyncio
async def test_cv_ingestion_pipeline_auto_fallback_on_primary_failure():
    pipeline = CVIngestionPipeline(
        parser=MockParser(),
        primary_extractor=MockFailingExtractor(),
        fallback_extractor=MockSuccessfulExtractor(name="Fallback Extractor Result"),
        enable_fallback=True,
    )

    raw_text, profile = await pipeline.process_bytes(b"%PDF-1.4 sample bytes")

    assert "Nguyen Van A" in raw_text
    assert profile.full_name == "Fallback Extractor Result"


@pytest.mark.asyncio
async def test_cv_ingestion_pipeline_raises_when_both_fail():
    pipeline = CVIngestionPipeline(
        parser=MockParser(),
        primary_extractor=MockFailingExtractor(),
        fallback_extractor=MockFailingExtractor(),
        enable_fallback=True,
    )

    with pytest.raises(ValueError) as exc_info:
        await pipeline.process_bytes(b"%PDF-1.4 sample bytes")

    assert "thất bại trên cả 2 nhà cung cấp" in str(exc_info.value)
