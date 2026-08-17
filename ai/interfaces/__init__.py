"""Abstract interfaces for document parsers and AI extractors (SOLID principles)."""

from ai.interfaces.parser import BaseDocumentParser
from ai.interfaces.extractor import BaseProfileExtractor

__all__ = ["BaseDocumentParser", "BaseProfileExtractor"]
