"""Parsers package."""

from ai.parsers.pdf_parser import (
    PyMuPDFParser,
    PDFParsingError,
    PDFScanDetectedError,
    PDFInvalidFormatError,
)
from ai.parsers.docx_parser import (
    DocxDocumentParser,
    DocxParsingError,
    DocxInvalidFormatError,
)

__all__ = [
    "PyMuPDFParser",
    "PDFParsingError",
    "PDFScanDetectedError",
    "PDFInvalidFormatError",
    "DocxDocumentParser",
    "DocxParsingError",
    "DocxInvalidFormatError",
]
