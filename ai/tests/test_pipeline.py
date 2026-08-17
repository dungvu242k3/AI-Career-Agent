"""Unit tests for CVIngestionPipeline and auto-healing."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from ai.pipeline import CVIngestionPipeline
from ai.interfaces.parser import BaseDocumentParser
from ai.interfaces.extractor import BaseProfileExtractor
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy


class MockParser(BaseDocumentParser):
    def extract_text_from_bytes(self, content_bytes: bytes, filename: str = "upload.pdf") -> str:
        return "Nguyen Van A\nPython Developer"

    def extract_text_from_file(self, file_path) -> str:
        return "Nguyen Van A\nPython Developer"


class MockExtractor(BaseProfileExtractor):
    async def extract_profile(self, raw_text: str) -> CandidateProfile:
        return CandidateProfile(
            personal_info=PersonalInfo(
                full_name="Nguyen Van A",
                email="an@test.com",
            ),
            summary=SummarySection(detected_title="Python Developer"),
            skills_taxonomy=SkillsTaxonomy(
                programming_languages=["Python", "Go"],
            ),
        )


@pytest.mark.asyncio
async def test_cv_ingestion_pipeline_execution():
    pipeline = CVIngestionPipeline(
        parser=MockParser(),
        extractor=MockExtractor(),
    )

    raw_text, profile = await pipeline.process_bytes(b"%PDF-1.4 sample bytes")

    assert "Nguyen Van A" in raw_text
    assert profile.full_name == "Nguyen Van A"
    assert profile.title == "Python Developer"
    assert "Python" in profile.skills_taxonomy.programming_languages
