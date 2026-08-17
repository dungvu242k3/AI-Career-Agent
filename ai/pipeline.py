"""High-level CV Ingestion Pipeline Orchestrator (Dependency Inversion Principle).

Coordinates Document Parser -> Extraction Engine -> Canonical Validation.
"""

from pathlib import Path
from ai.interfaces.parser import BaseDocumentParser
from ai.interfaces.extractor import BaseProfileExtractor
from ai.parsers.pdf_parser import PyMuPDFParser
from ai.extractors.cv_extractor import GeminiCVExtractor
from ai.models.candidate import CandidateProfile


class CVIngestionPipeline:
    """Orchestrates parsing, AI extraction, and normalization of CV documents."""

    def __init__(
        self,
        parser: BaseDocumentParser | None = None,
        extractor: BaseProfileExtractor | None = None,
    ):
        self.parser = parser or PyMuPDFParser()
        self.extractor = extractor or GeminiCVExtractor()

    async def process_bytes(
        self,
        content_bytes: bytes,
        filename: str = "upload.pdf",
    ) -> tuple[str, CandidateProfile]:
        """Execute end-to-end ingestion pipeline from raw PDF bytes.

        Returns:
            Tuple of (cleaned_raw_text, candidate_profile).
        """
        # Step 1: Extract and de-noise document text
        raw_text = self.parser.extract_text_from_bytes(content_bytes, filename=filename)

        # Step 2: Extract structured profile via LLM
        profile = await self.extractor.extract_profile(raw_text)

        return raw_text, profile

    async def process_file(
        self,
        file_path: str | Path,
    ) -> tuple[str, CandidateProfile]:
        """Execute end-to-end ingestion pipeline from a local file path."""
        path = Path(file_path)
        content_bytes = path.read_bytes()
        return await self.process_bytes(content_bytes, filename=path.name)


def get_default_ingestion_pipeline() -> CVIngestionPipeline:
    """Factory for standard production pipeline."""
    return CVIngestionPipeline(
        parser=PyMuPDFParser(),
        extractor=GeminiCVExtractor(),
    )
