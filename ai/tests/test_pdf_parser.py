"""Unit tests for PyMuPDFParser."""

import pytest
import fitz  # PyMuPDF
from ai.parsers.pdf_parser import PyMuPDFParser, PDFScanDetectedError, PDFInvalidFormatError


def _create_sample_pdf_bytes(text_blocks: list[tuple[float, float, str]], page_width: float = 600, page_height: float = 800) -> bytes:
    """Helper to generate in-memory synthetic PDF with precise text placement."""
    doc = fitz.open()
    page = doc.new_page(width=page_width, height=page_height)
    for x, y, text in text_blocks:
        page.insert_text(fitz.Point(x, y), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pdf_parser_single_column():
    parser = PyMuPDFParser()
    sample_text = (
        "Nguyen Van A\n"
        "AI Engineer\n"
        "- Experience in Python and FastAPI\n"
        "- Built enterprise RAG pipelines"
    )
    pdf_bytes = _create_sample_pdf_bytes([(50, 50, sample_text)])
    extracted = parser.extract_text_from_bytes(pdf_bytes, filename="test.pdf")

    assert "Nguyen Van A" in extracted
    assert "AI Engineer" in extracted
    assert "Python and FastAPI" in extracted


def test_pdf_parser_two_column_layout_preservation():
    parser = PyMuPDFParser()
    # Left column at x=50 (Skills & Info), Right column at x=350 (Experience)
    blocks = [
        (50, 50, "Nguyen Van A - Resume Header"),
        (50, 150, "SKILLS\n- Python\n- Go\n- Docker"),
        (50, 250, "EDUCATION\nHUST 2019-2023"),
        (350, 150, "WORK EXPERIENCE\nCompany VNG - AI Engineer"),
        (350, 250, "PROJECTS\nAI Career Agent built with FastAPI"),
    ]
    pdf_bytes = _create_sample_pdf_bytes(blocks)
    extracted = parser.extract_text_from_bytes(pdf_bytes)

    assert "Nguyen Van A" in extracted
    assert "SKILLS" in extracted
    assert "WORK EXPERIENCE" in extracted


def test_pdf_parser_scanned_pdf_rejection():
    parser = PyMuPDFParser()
    # Less than 50 printable characters
    pdf_bytes = _create_sample_pdf_bytes([(50, 50, "Short")])

    with pytest.raises(PDFScanDetectedError) as exc_info:
        parser.extract_text_from_bytes(pdf_bytes)
    assert "hình ảnh scan" in str(exc_info.value)


def test_pdf_parser_invalid_header_rejection():
    parser = PyMuPDFParser()
    corrupt_bytes = b"NOT_A_PDF_CONTENT_STREAM"

    with pytest.raises(PDFInvalidFormatError) as exc_info:
        parser.extract_text_from_bytes(corrupt_bytes)
    assert "%PDF" in str(exc_info.value)
