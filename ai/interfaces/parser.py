"""Abstract Base Document Parser Interface."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseDocumentParser(ABC):
    """Interface for document text extraction and de-noising (Open-Closed Principle)."""

    @abstractmethod
    def extract_text_from_bytes(self, content_bytes: bytes, filename: str = "upload.pdf") -> str:
        """Extract and clean text from raw document bytes."""
        pass

    @abstractmethod
    def extract_text_from_file(self, file_path: str | Path) -> str:
        """Extract and clean text from local file path."""
        pass
