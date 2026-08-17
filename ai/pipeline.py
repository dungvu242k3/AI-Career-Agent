"""High-level CV Ingestion Pipeline Orchestrator (Dependency Inversion & Multi-Provider Fallback).

Coordinates Document Parser -> Primary Extractor (OpenAI) -> Fallback Extractor (Gemini).
"""

import logging
from pathlib import Path
from ai.interfaces.parser import BaseDocumentParser
from ai.interfaces.extractor import BaseProfileExtractor
from ai.parsers.pdf_parser import PyMuPDFParser
from ai.extractors.openai_extractor import OpenAICVExtractor
from ai.extractors.cv_extractor import GeminiCVExtractor
from ai.models.candidate import CandidateProfile
from ai.config import get_ai_config

logger = logging.getLogger(__name__)


class CVIngestionPipeline:
    """Orchestrates parsing, AI extraction, and normalization of CV documents with multi-provider fallback."""

    def __init__(
        self,
        parser: BaseDocumentParser | None = None,
        primary_extractor: BaseProfileExtractor | None = None,
        fallback_extractor: BaseProfileExtractor | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.parser = parser or PyMuPDFParser()

        # Determine primary and fallback extractors
        if primary_extractor:
            self.primary_extractor = primary_extractor
        else:
            self.primary_extractor = (
                OpenAICVExtractor() if self.config.ai_provider == "openai" else GeminiCVExtractor()
            )

        if fallback_extractor:
            self.fallback_extractor = fallback_extractor
        else:
            self.fallback_extractor = (
                GeminiCVExtractor() if self.config.ai_provider == "openai" else OpenAICVExtractor()
            )

        self.enable_fallback = (
            enable_fallback if enable_fallback is not None else self.config.enable_fallback
        )

    async def process_bytes(
        self,
        content_bytes: bytes,
        filename: str = "upload.pdf",
    ) -> tuple[str, CandidateProfile]:
        """Execute end-to-end ingestion pipeline from raw PDF bytes with auto-fallback."""
        # Step 1: Extract and de-noise document text
        raw_text = self.parser.extract_text_from_bytes(content_bytes, filename=filename)

        # Step 2: Extract structured profile via Primary Provider (e.g. OpenAI)
        try:
            profile = await self.primary_extractor.extract_profile(raw_text)
            return raw_text, profile
        except Exception as primary_err:
            if not self.enable_fallback:
                raise

            logger.warning(
                "Primary extractor (%s) failed: %s. Initiating auto-fallback to secondary extractor (%s)...",
                self.primary_extractor.__class__.__name__,
                primary_err,
                self.fallback_extractor.__class__.__name__,
            )

            try:
                profile = await self.fallback_extractor.extract_profile(raw_text)
                logger.info(
                    "Auto-fallback to %s succeeded.",
                    self.fallback_extractor.__class__.__name__,
                )
                return raw_text, profile
            except Exception as fallback_err:
                logger.error("Both primary and fallback extractors failed. Fallback error: %s", fallback_err)
                raise ValueError(
                    f"Trích xuất AI thất bại trên cả 2 nhà cung cấp (Lỗi chính: {primary_err} | Lỗi dự phòng: {fallback_err})"
                )

    async def process_file(
        self,
        file_path: str | Path,
    ) -> tuple[str, CandidateProfile]:
        """Execute end-to-end ingestion pipeline from a local file path."""
        path = Path(file_path)
        content_bytes = path.read_bytes()
        return await self.process_bytes(content_bytes, filename=path.name)


def get_default_ingestion_pipeline() -> CVIngestionPipeline:
    """Factory for standard production pipeline configured via environment settings."""
    return CVIngestionPipeline()
