"""Safe in-memory Job Description parsing with provider-neutral execution."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import re
from typing import Literal

from google.genai import types
from pydantic import ValidationError

from ai.client import get_gemini_client, get_openai_client
from ai.config import get_ai_config
from ai.execution import AIStage, get_ai_executor
from ai.models.jd import JDProfile
from ai.parsers.docx_parser import DOCX_MAGIC_BYTES, DocxDocumentParser
from ai.parsers.pdf_parser import PyMuPDFParser
from ai.privacy import sanitize_llm_input
from ai.prompts import load_composed_prompt


logger = logging.getLogger(__name__)
MAX_JD_TEXT_LENGTH = 10_000
MIN_JD_TEXT_LENGTH = 15
MAX_JD_FILE_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_JD_EXTENSIONS = {".pdf", ".docx"}


class JDParser:
    def __init__(
        self,
        ai_provider: Literal["openai", "gemini"] | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.ai_provider = ai_provider or self.config.ai_provider
        self.enable_fallback = self.config.enable_fallback if enable_fallback is None else enable_fallback
        self.pdf_parser = PyMuPDFParser()
        self.docx_parser = DocxDocumentParser()
        self._executor = get_ai_executor()
        self.system_instruction = load_composed_prompt("system_prompt.md", "jd_extraction.md")

    @staticmethod
    def _sanitize_text(text: str) -> str:
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text or "").strip()
        if len(cleaned) > MAX_JD_TEXT_LENGTH:
            logger.warning("JD text exceeded length cap; truncating before LLM execution")
            cleaned = cleaned[:MAX_JD_TEXT_LENGTH]
        return cleaned

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            normalized = item.strip()
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                result.append(normalized)
        return result

    def _normalize(self, jd: JDProfile, raw_text: str) -> JDProfile:
        jd.job_title = jd.job_title.strip() if jd.job_title else "Job opening"
        jd.company_name = jd.company_name.strip() if jd.company_name else None
        jd.must_have_skills = self._deduplicate(jd.must_have_skills)
        jd.nice_to_have_skills = self._deduplicate(jd.nice_to_have_skills)
        jd.responsibilities = [item.strip() for item in jd.responsibilities if item.strip()]
        jd.benefits = [item.strip() for item in jd.benefits if item.strip()]
        jd.raw_text = raw_text
        return jd

    # Compatibility name for callers that need normalization without a model
    # call. It performs no speculative enrichment.
    def _auto_heal_jd(self, jd: JDProfile, raw_text: str) -> JDProfile:
        return self._normalize(jd, raw_text)

    async def _extract_with_openai(self, raw_text: str) -> JDProfile:
        completion = await get_openai_client().beta.chat.completions.parse(
            model=self.config.model_for("extraction", "openai"),
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": f"<job_description>\n{raw_text}\n</job_description>"},
            ],
            response_format=JDProfile,
            temperature=self.config.extraction_temperature,
            max_tokens=self.config.extraction_max_tokens,
        )
        parsed = completion.choices[0].message.parsed
        if not parsed:
            raise ValueError("OpenAI returned no structured JD")
        return self._normalize(parsed, raw_text)

    async def _extract_with_gemini(self, raw_text: str) -> JDProfile:
        response = await get_gemini_client().aio.models.generate_content(
            model=self.config.model_for("extraction", "gemini"),
            contents=f"<job_description>\n{raw_text}\n</job_description>",
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=JDProfile,
                temperature=self.config.extraction_temperature,
                max_output_tokens=self.config.extraction_max_tokens,
            ),
        )
        if not response.text:
            raise ValueError("Gemini returned no structured JD")
        raw_json = re.sub(r"^```(?:json)?\n?|\n?```$", "", response.text.strip())
        try:
            return self._normalize(JDProfile.model_validate(json.loads(raw_json)), raw_text)
        except (json.JSONDecodeError, ValidationError) as error:
            raise ValueError("Gemini returned an invalid JD schema") from error

    async def parse_jd_text(self, raw_text: str) -> JDProfile:
        cleaned_text = self._sanitize_text(raw_text)
        if len(cleaned_text) < MIN_JD_TEXT_LENGTH:
            raise ValueError("Nội dung JD không được để trống hoặc quá ngắn")
        safe_text = sanitize_llm_input(cleaned_text)
        primary = self._extract_with_openai if self.ai_provider == "openai" else self._extract_with_gemini
        fallback = self._extract_with_gemini if self.ai_provider == "openai" else self._extract_with_openai
        outcome = await self._executor.run(
            stage=AIStage.EXTRACTION,
            primary_provider=self.ai_provider,
            primary=lambda: primary(safe_text),
            fallback_provider=("gemini" if self.ai_provider == "openai" else "openai") if self.enable_fallback else None,
            fallback=(lambda: fallback(safe_text)) if self.enable_fallback else None,
            input_chars=len(safe_text),
            primary_model=self.config.model_for("extraction", self.ai_provider),
            fallback_model=self.config.model_for("extraction", "gemini" if self.ai_provider == "openai" else "openai"),
        )
        logger.info("JD extraction completed trace_id=%s provider=%s", outcome.trace_id, outcome.provider)
        return outcome.value

    async def parse_jd_file(self, content_bytes: bytes, filename: str) -> JDProfile:
        if not filename.strip() or Path(filename).suffix.lower() not in ALLOWED_JD_EXTENSIONS:
            raise ValueError("Chỉ chấp nhận tệp định dạng PDF hoặc DOCX cho JD")
        if len(content_bytes) < 4 or len(content_bytes) > MAX_JD_FILE_SIZE_BYTES:
            raise ValueError("Tệp JD rỗng hoặc bị lỗi, hoặc vượt quá giới hạn cho phép (2MB)")
        if filename.lower().endswith(".docx") or content_bytes.startswith(DOCX_MAGIC_BYTES):
            extracted = self.docx_parser.extract_text_from_bytes(content_bytes, filename)
        else:
            extracted = self.pdf_parser.extract_text_from_bytes(content_bytes, filename)
        return await self.parse_jd_text(extracted)


def get_default_jd_parser() -> JDParser:
    return JDParser()
