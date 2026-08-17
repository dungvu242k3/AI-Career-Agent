"""PDF Parser Service — Extract raw text from PDF files using PyMuPDF."""

import fitz  # PyMuPDF
from pathlib import Path


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract all text content from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        ValueError: If the file is not a valid PDF or is empty.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    doc = fitz.open(str(path))

    if doc.page_count == 0:
        raise ValueError("PDF file has no pages")

    text_parts: list[str] = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            text_parts.append(text.strip())

    doc.close()

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError("PDF file contains no extractable text (possibly scanned/image-only)")

    return full_text


def extract_text_from_bytes(pdf_bytes: bytes, filename: str = "upload.pdf") -> str:
    """Extract text from PDF bytes (for file upload without saving).

    Args:
        pdf_bytes: Raw PDF file content.
        filename: Original filename for error messages.

    Returns:
        Extracted text as a single string.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    if doc.page_count == 0:
        raise ValueError(f"PDF '{filename}' has no pages")

    text_parts: list[str] = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            text_parts.append(text.strip())

    doc.close()

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError(f"PDF '{filename}' contains no extractable text")

    return full_text
