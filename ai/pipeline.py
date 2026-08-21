"""CV ingestion orchestration with safe LLM execution and provider fallback."""

from __future__ import annotations

import logging
from pathlib import Path

from ai.config import get_ai_config
from ai.execution import AIStage, get_ai_executor
from ai.extractors.cv_extractor import GeminiCVExtractor
from ai.extractors.openai_extractor import OpenAICVExtractor
from ai.interfaces.extractor import BaseProfileExtractor
from ai.interfaces.parser import BaseDocumentParser
from ai.models.candidate import CandidateProfile
from ai.parsers.docx_parser import DOCX_MAGIC_BYTES, DocxDocumentParser
from ai.parsers.pdf_parser import PyMuPDFParser
from ai.privacy import redact_cv_for_llm, restore_extracted_contact


logger = logging.getLogger(__name__)


class CVIngestionPipeline:
    """Parse a CV then run a privacy-safe structured extraction."""

    def __init__(
        self,
        parser: BaseDocumentParser | None = None,
        primary_extractor: BaseProfileExtractor | None = None,
        fallback_extractor: BaseProfileExtractor | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self._custom_parser = parser
        self.pdf_parser = PyMuPDFParser()
        self.docx_parser = DocxDocumentParser()
        self.primary_extractor = primary_extractor or (
            OpenAICVExtractor() if self.config.ai_provider == "openai" else GeminiCVExtractor()
        )
        self.fallback_extractor = fallback_extractor or (
            GeminiCVExtractor() if self.config.ai_provider == "openai" else OpenAICVExtractor()
        )
        self.enable_fallback = self.config.enable_fallback if enable_fallback is None else enable_fallback
        self._executor = get_ai_executor()

    def _resolve_parser(self, content_bytes: bytes, filename: str) -> BaseDocumentParser:
        if self._custom_parser:
            return self._custom_parser
        if filename.lower().endswith(".docx") or content_bytes.startswith(DOCX_MAGIC_BYTES):
            return self.docx_parser
        return self.pdf_parser

    async def process_bytes(self, content_bytes: bytes, filename: str = "upload.pdf") -> tuple[str, CandidateProfile]:
        parser = self._resolve_parser(content_bytes, filename)
        raw_text = parser.extract_text_from_bytes(content_bytes, filename=filename)

        # Never cache CV extraction: the output has personal data.  The LLM
        # only receives the guardrailed text; contact values are recovered by
        # local deterministic parsing after structured extraction.
        safe_text, local_name = redact_cv_for_llm(raw_text)
        primary_provider = self.config.ai_provider
        fallback_provider = "gemini" if primary_provider == "openai" else "openai"
        result = await self._executor.run(
            stage=AIStage.EXTRACTION,
            primary_provider=primary_provider,
            primary=lambda: self.primary_extractor.extract_profile(safe_text),
            fallback_provider=fallback_provider if self.enable_fallback else None,
            fallback=(lambda: self.fallback_extractor.extract_profile(safe_text)) if self.enable_fallback else None,
            input_chars=len(safe_text),
            primary_model=self.config.model_for("extraction", primary_provider),
            fallback_model=self.config.model_for("extraction", fallback_provider),
        )
        profile = restore_extracted_contact(result.value, raw_text, full_name=local_name)
        logger.info("CV extraction completed trace_id=%s provider=%s", result.trace_id, result.provider)
        return raw_text, profile

    async def process_file(self, file_path: str | Path) -> tuple[str, CandidateProfile]:
        path = Path(file_path)
        return await self.process_bytes(path.read_bytes(), filename=path.name)


def get_default_ingestion_pipeline() -> CVIngestionPipeline:
    return CVIngestionPipeline()
