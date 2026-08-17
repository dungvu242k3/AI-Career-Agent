"""PyMuPDF Document Parser — Spatial layout extraction, de-noising, and scanned PDF detection.

Implements BaseDocumentParser.
"""

import re
import unicodedata
from pathlib import Path
import fitz  # PyMuPDF

from ai.interfaces.parser import BaseDocumentParser
from ai.config import get_ai_config


class PDFParsingError(ValueError):
    """Base exception for PDF parsing failures."""
    pass


class PDFScanDetectedError(PDFParsingError):
    """Raised when PDF has no extractable text layer (scanned or image-only)."""
    pass


class PDFInvalidFormatError(PDFParsingError):
    """Raised when file is corrupt, not a PDF, or encrypted."""
    pass


class PyMuPDFParser(BaseDocumentParser):
    """Production PyMuPDF parser with 2-column layout spatial block sorting."""

    def __init__(self):
        self.config = get_ai_config()

    def _normalize_text(self, text: str) -> str:
        """Normalize Unicode (NFC), remove font glyphs, and standardize bullet points."""
        if not text:
            return ""

        # Normalize Unicode to NFC (resolves Vietnamese decomposed tone marks)
        text = unicodedata.normalize("NFC", text)

        # Remove Private Use Area characters (common font-icon glyphs like \uf0e0, \uf095)
        text = re.sub(r"[\ue000-\uf8ff]", "", text)

        # Standardize bullet symbols into clean markdown '- '
        text = re.sub(r"^[ \t]*[•◦▪➢✦★*+·►■-][ \t]+", "- ", text, flags=re.MULTILINE)

        # Clean multiple consecutive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _extract_page_blocks(self, page: fitz.Page) -> list[str]:
        """Extract text blocks using spatial sorting to handle multi-column layouts."""
        raw_blocks = page.get_text("blocks")
        if not raw_blocks:
            return []

        text_blocks = [b for b in raw_blocks if b[6] == 0 and b[4].strip()]
        if not text_blocks:
            return []

        page_width = page.rect.width
        midpoint = page_width / 2.0

        left_blocks = []
        right_blocks = []
        spanning_blocks = []

        for b in text_blocks:
            x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
            if x1 <= midpoint * 1.15:
                left_blocks.append(b)
            elif x0 >= midpoint * 0.85:
                right_blocks.append(b)
            else:
                spanning_blocks.append(b)

        # If substantial content is on both sides, sort left column first then right column
        if len(left_blocks) >= 2 and len(right_blocks) >= 2:
            spanning_blocks.sort(key=lambda b: (b[1], b[0]))
            left_blocks.sort(key=lambda b: (b[1], b[0]))
            right_blocks.sort(key=lambda b: (b[1], b[0]))
            ordered_blocks = spanning_blocks + left_blocks + right_blocks
        else:
            ordered_blocks = sorted(text_blocks, key=lambda b: (b[1], b[0]))

        return [self._normalize_text(b[4]) for b in ordered_blocks if b[4].strip()]

    def extract_text_from_bytes(self, content_bytes: bytes, filename: str = "upload.pdf") -> str:
        """Extract and de-noise text from raw PDF bytes."""
        if not content_bytes.startswith(b"%PDF"):
            raise PDFInvalidFormatError(f"Tệp '{filename}' không phải là định dạng PDF hợp lệ (thiếu header %PDF).")

        try:
            doc = fitz.open(stream=content_bytes, filetype="pdf")
        except Exception as e:
            raise PDFInvalidFormatError(f"Không thể mở tệp PDF '{filename}': {e}")

        if doc.is_encrypted:
            doc.close()
            raise PDFInvalidFormatError(f"Tệp PDF '{filename}' đã bị khóa bằng mật khẩu. Vui lòng mở khóa trước khi tải lên.")

        page_count = doc.page_count
        if page_count == 0:
            doc.close()
            raise PDFInvalidFormatError(f"Tệp PDF '{filename}' không chứa trang nào.")
        if page_count > self.config.max_pdf_pages:
            doc.close()
            raise PDFInvalidFormatError(f"Tệp PDF '{filename}' có {page_count} trang (vượt quá giới hạn tối đa {self.config.max_pdf_pages} trang).")

        all_page_texts: list[str] = []
        for page_idx in range(page_count):
            page = doc[page_idx]
            page_blocks = self._extract_page_blocks(page)
            if page_blocks:
                all_page_texts.append("\n\n".join(page_blocks))

        doc.close()

        full_text = "\n\n---\n\n".join(all_page_texts).strip()

        # Check if scanned / image-only (< min_text_length)
        clean_char_count = len(re.sub(r"\s+", "", full_text))
        if clean_char_count < self.config.min_text_length:
            raise PDFScanDetectedError(
                "CV của bạn ở dạng hình ảnh scan (không có lớp chữ). "
                "Vui lòng xuất lại tệp PDF trực tiếp từ Word, Canva hoặc Google Docs để AI có thể đọc chính xác."
            )

        return full_text

    def extract_text_from_file(self, file_path: str | Path) -> str:
        """Extract text from local file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Tệp không tồn tại: {path}")

        return self.extract_text_from_bytes(path.read_bytes(), filename=path.name)
