"""Job Description (JD) Parser — In-memory text extraction, multi-provider LLM parsing, and normalization.

Supports:
1. Raw Text Parsing (Paste input)
2. File Parsing (PDF / DOCX in-memory with instant buffer release)
3. OpenAI (Primary) + Gemini (Fallback) multi-provider architecture
"""

import json
import logging
from pathlib import Path
import re
from typing import Literal
from google.genai import types
from pydantic import ValidationError

from ai.config import get_ai_config
from ai.client import get_openai_client, get_gemini_client
from ai.models.jd import JDProfile
from ai.parsers.docx_parser import DocxDocumentParser, DOCX_MAGIC_BYTES
from ai.parsers.pdf_parser import PyMuPDFParser
from ai.prompts import load_composed_prompt

logger = logging.getLogger(__name__)

# Constants
MAX_JD_TEXT_LENGTH = 10_000
MIN_JD_TEXT_LENGTH = 15
MAX_JD_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB
ALLOWED_JD_EXTENSIONS = {".pdf", ".docx"}


class JDParser:
    """Production-grade In-Memory Job Description Parser with multi-provider LLM fallback."""

    def __init__(
        self,
        ai_provider: Literal["openai", "gemini"] | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.ai_provider = ai_provider or self.config.ai_provider
        self.enable_fallback = (
            enable_fallback if enable_fallback is not None else self.config.enable_fallback
        )

        self.pdf_parser = PyMuPDFParser()
        self.docx_parser = DocxDocumentParser()

        self.system_instruction = load_composed_prompt(
            "system_prompt.md",
            "jd_extraction.md",
        )

    def _sanitize_text(self, text: str) -> str:
        """Strip control characters, trim whitespace, and enforce maximum length."""
        if not text:
            return ""
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text).strip()
        if len(cleaned) > MAX_JD_TEXT_LENGTH:
            logger.warning(
                "JD text length (%d) exceeded limit (%d). Truncating.",
                len(cleaned),
                MAX_JD_TEXT_LENGTH,
            )
            cleaned = cleaned[:MAX_JD_TEXT_LENGTH]
        return cleaned

    def _deduplicate_list(self, items: list[str]) -> list[str]:
        """Deduplicate string lists preserving order and stripping whitespace."""
        seen = set()
        cleaned = []
        for item in items:
            norm = item.strip()
            if norm and norm.lower() not in seen:
                seen.add(norm.lower())
                cleaned.append(norm)
        return cleaned

    def _auto_heal_jd(self, jd: JDProfile, raw_text: str) -> JDProfile:
        """Sanitize and normalize parsed JDProfile fields."""
        jd.job_title = jd.job_title.strip() if jd.job_title else "Vị trí tuyển dụng"
        jd.company_name = jd.company_name.strip() if jd.company_name else None
        jd.must_have_skills = self._deduplicate_list(jd.must_have_skills)
        jd.nice_to_have_skills = self._deduplicate_list(jd.nice_to_have_skills)
        jd.responsibilities = [r.strip() for r in jd.responsibilities if r.strip()]
        jd.benefits = [b.strip() for b in jd.benefits if b.strip()]
        jd.raw_text = raw_text
        return jd

    async def _extract_with_openai(self, raw_text: str) -> JDProfile:
        """Extract structured JDProfile using OpenAI Structured Outputs (gpt-4o-mini)."""
        client = get_openai_client()
        user_content = f"<job_description>\n{raw_text}\n</job_description>"

        completion = await client.beta.chat.completions.parse(
            model=self.config.openai_extraction_model,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": user_content},
            ],
            response_format=JDProfile,
            temperature=self.config.extraction_temperature,
            max_tokens=self.config.extraction_max_tokens,
        )

        parsed_jd = completion.choices[0].message.parsed
        if not parsed_jd:
            refusal = getattr(completion.choices[0].message, "refusal", None)
            if refusal:
                raise ValueError(f"OpenAI từ chối phân tích JD: {refusal}")
            raise ValueError("OpenAI trả về phản hồi rỗng khi trích xuất JD.")

        return self._auto_heal_jd(parsed_jd, raw_text)

    async def _extract_with_gemini(self, raw_text: str) -> JDProfile:
        """Extract structured JDProfile using Google Gemini response schema."""
        client = get_gemini_client()
        user_content = f"<job_description>\n{raw_text}\n</job_description>"

        response = await client.aio.models.generate_content(
            model=self.config.gemini_flash_lite_model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=JDProfile,
                temperature=self.config.extraction_temperature,
                max_output_tokens=self.config.extraction_max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Gemini trả về phản hồi rỗng khi trích xuất JD.")

        raw_json_str = response.text.strip()
        if raw_json_str.startswith("```"):
            raw_json_str = re.sub(r"^```(?:json)?\n?", "", raw_json_str)
            raw_json_str = re.sub(r"\n?```$", "", raw_json_str)

        try:
            data = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI trả về định dạng JSON không hợp lệ: {e}")

        try:
            jd = JDProfile.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Dữ liệu trích xuất từ JD không đúng cấu trúc quy định: {e}")

        return self._auto_heal_jd(jd, raw_text)

    async def parse_jd_text(self, raw_text: str) -> JDProfile:
        """Parse raw JD text into structured JDProfile with multi-provider fallback."""
        cleaned_text = self._sanitize_text(raw_text)
        if len(cleaned_text) < MIN_JD_TEXT_LENGTH:
            raise ValueError("Nội dung mô tả công việc (JD) không được để trống hoặc quá ngắn.")

        primary_fn = (
            self._extract_with_openai
            if self.ai_provider == "openai"
            else self._extract_with_gemini
        )
        fallback_fn = (
            self._extract_with_gemini
            if self.ai_provider == "openai"
            else self._extract_with_openai
        )

        try:
            return await primary_fn(cleaned_text)
        except Exception as primary_err:
            if not self.enable_fallback:
                logger.error("Primary JD extraction failed: %s", primary_err)
                raise

            logger.warning(
                "Primary JD extractor failed: %s. Initiating fallback...",
                primary_err,
            )
            try:
                jd = await fallback_fn(cleaned_text)
                logger.info("Fallback JD extractor succeeded.")
                return jd
            except Exception as fallback_err:
                logger.error("Both primary and fallback JD extractors failed: %s", fallback_err)
                raise ValueError(
                    f"Trích xuất JD thất bại trên cả 2 nhà cung cấp AI: {primary_err} | {fallback_err}"
                )

    async def parse_jd_file(self, content_bytes: bytes, filename: str) -> JDProfile:
        """Extract text from in-memory PDF/Word JD file and parse into JDProfile, freeing memory immediately."""
        if not filename or not filename.strip():
            raise ValueError("Tên tệp không hợp lệ.")

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_JD_EXTENSIONS:
            raise ValueError("Chỉ chấp nhận tệp định dạng PDF (.pdf) hoặc Microsoft Word (.docx).")

        if len(content_bytes) > MAX_JD_FILE_SIZE_BYTES:
            raise ValueError(
                f"Kích thước tệp JD ({len(content_bytes) / (1024*1024):.1f}MB) vượt quá giới hạn cho phép (2MB)."
            )

        if len(content_bytes) < 4:
            raise ValueError("Tệp JD rỗng hoặc bị lỗi.")

        # In-memory text extraction
        if ext == ".docx" or content_bytes.startswith(DOCX_MAGIC_BYTES):
            extracted_text = self.docx_parser.extract_text_from_bytes(content_bytes, filename=filename)
        else:
            extracted_text = self.pdf_parser.extract_text_from_bytes(content_bytes, filename=filename)

        # Explicitly release raw bytes buffer immediately
        del content_bytes

        return await self.parse_jd_text(extracted_text)


def get_default_jd_parser() -> JDParser:
    """Factory function for default JDParser instance."""
    return JDParser()
