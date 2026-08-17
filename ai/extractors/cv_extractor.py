"""Gemini CV Extractor — Converts raw text to structured CandidateProfile (v3).

Implements BaseProfileExtractor with prompt loading, Pydantic auto-healing,
non-blocking async API, prompt injection defense, and resilient validation.
"""

import json
import logging
import re
from datetime import datetime
from google.genai import types
from pydantic import ValidationError

from ai.interfaces.extractor import BaseProfileExtractor
from ai.models.candidate import CandidateProfile
from ai.prompts import load_prompt
from ai.config import get_ai_config
from ai.client import get_gemini_client

logger = logging.getLogger(__name__)


class GeminiCVExtractor(BaseProfileExtractor):
    """Production structured CV extractor powered by Gemini Flash."""

    def __init__(self):
        self.config = get_ai_config()
        self.system_instruction = load_prompt("extract_cv.txt")

    def _sanitize_url(self, url: str | None) -> str | None:
        """Ensure URLs have a valid scheme and are cleaned."""
        if not url:
            return None
        url = url.strip()
        if not url:
            return None
        if not url.startswith(("http://", "https://")):
            return f"https://{url}"
        return url

    def _sanitize_phone(self, phone: str | None) -> str | None:
        """Normalize phone numbers removing unexpected characters."""
        if not phone:
            return None
        phone = re.sub(r"[^\d+()\-\s.]", "", phone).strip()
        return phone if len(phone) >= 7 else None

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

    def _estimate_total_experience(self, work_history) -> float:
        """Estimate cumulative experience in years from work history dates by merging overlapping intervals."""
        current_year = datetime.now().year
        current_month = datetime.now().month
        intervals: list[tuple[int, int]] = []

        for item in work_history:
            try:
                start_parts = [int(p) for p in re.findall(r"\d+", str(item.start_date))]
                if not start_parts:
                    continue
                start_y = start_parts[0]
                start_m = start_parts[1] if len(start_parts) > 1 else 1

                if item.is_current or not item.end_date:
                    end_y, end_m = current_year, current_month
                else:
                    end_parts = [int(p) for p in re.findall(r"\d+", str(item.end_date))]
                    if not end_parts:
                        continue
                    end_y = end_parts[0]
                    end_m = end_parts[1] if len(end_parts) > 1 else 12

                start_idx = start_y * 12 + start_m
                end_idx = end_y * 12 + end_m
                if end_idx >= start_idx:
                    intervals.append((start_idx, end_idx))
            except Exception:
                continue

        if not intervals:
            return 0.0

        # Merge overlapping time spans
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for current in intervals[1:]:
            prev_start, prev_end = merged[-1]
            if current[0] <= prev_end:
                merged[-1] = (prev_start, max(prev_end, current[1]))
            else:
                merged.append(current)

        total_months = sum((end - start + 1) for start, end in merged)
        return round(total_months / 12.0, 1)

    def _auto_heal_profile(self, data: dict) -> CandidateProfile:
        """Apply auto-healing transformations before Pydantic validation."""
        if "personal_info" not in data or not isinstance(data["personal_info"], dict):
            data["personal_info"] = {
                "full_name": data.get("full_name", "Ứng viên"),
                "email": data.get("email"),
                "phone": data.get("phone"),
                "location": data.get("location"),
            }

        pinfo = data["personal_info"]
        if not pinfo.get("full_name") or not str(pinfo["full_name"]).strip():
            pinfo["full_name"] = "Ứng viên"

        pinfo["linkedin_url"] = self._sanitize_url(pinfo.get("linkedin_url"))
        pinfo["github_url"] = self._sanitize_url(pinfo.get("github_url"))
        pinfo["portfolio_url"] = self._sanitize_url(pinfo.get("portfolio_url"))
        pinfo["phone"] = self._sanitize_phone(pinfo.get("phone"))

        # Deduplicate taxonomy skills
        if "skills_taxonomy" in data and isinstance(data["skills_taxonomy"], dict):
            for category, skill_list in data["skills_taxonomy"].items():
                if isinstance(skill_list, list):
                    data["skills_taxonomy"][category] = self._deduplicate_list(skill_list)

        profile = CandidateProfile.model_validate(data)

        # Sanitize project URLs
        for proj in profile.projects:
            proj.url = self._sanitize_url(proj.url)

        # Auto-calculate experience years if missing or 0.0
        if profile.metadata.total_experience_years == 0.0 and profile.work_experience:
            calculated_years = self._estimate_total_experience(profile.work_experience)
            if calculated_years > 0:
                profile.metadata.total_experience_years = calculated_years

        return profile

    async def extract_profile(self, raw_text: str) -> CandidateProfile:
        """Extract structured CandidateProfile from raw text via non-blocking async Gemini call."""
        client = get_gemini_client()

        # Prompt Injection Defense: Send System Instructions separately and encapsulate raw document
        user_content = f"<cv_document>\n{raw_text}\n</cv_document>"

        try:
            response = await client.aio.models.generate_content(
                model=self.config.extraction_model,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    temperature=self.config.extraction_temperature,
                    max_output_tokens=self.config.extraction_max_tokens,
                ),
            )
        except Exception as e:
            logger.error("Error during Gemini API call: %s", e)
            raise ValueError(f"Lỗi khi kết nối với Gemini AI: {e}")

        if not response.text:
            raise ValueError("Gemini trả về phản hồi rỗng khi trích xuất CV.")

        raw_json_str = response.text.strip()
        if raw_json_str.startswith("```"):
            raw_json_str = re.sub(r"^```(?:json)?\n?", "", raw_json_str)
            raw_json_str = re.sub(r"\n?```$", "", raw_json_str)

        try:
            data = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            logger.error("JSON decode error from LLM output: %s", e)
            raise ValueError(f"AI trả về định dạng JSON không hợp lệ: {e}")

        try:
            return self._auto_heal_profile(data)
        except ValidationError as e:
            logger.error("Pydantic validation error: %s", e)
            raise ValueError(f"Dữ liệu trích xuất từ CV không đúng cấu trúc quy định: {e}")
