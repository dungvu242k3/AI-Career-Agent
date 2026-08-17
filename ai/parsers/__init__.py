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
from ai.parsers.jd_parser import (
    JDParser,
    get_default_jd_parser,
)

__all__ = [
    "PyMuPDFParser",
    "PDFParsingError",
    "PDFScanDetectedError",
    "PDFInvalidFormatError",
    "DocxDocumentParser",
    "DocxParsingError",
    "DocxInvalidFormatError",
    "JDParser",
    "get_default_jd_parser",
]
