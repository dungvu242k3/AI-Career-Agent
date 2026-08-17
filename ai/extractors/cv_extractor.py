"""Gemini CV Extractor — Converts raw text to structured CandidateProfile (v3).

Implements BaseProfileExtractor with prompt loading, Pydantic auto-healing,
and resilient validation.
"""

import json
import re
from datetime import datetime
from google.genai import types

from ai.interfaces.extractor import BaseProfileExtractor
from ai.models.candidate import CandidateProfile
from ai.prompts import load_prompt
from ai.config import get_ai_config
from ai.client import get_gemini_client


class GeminiCVExtractor(BaseProfileExtractor):
    """Production structured CV extractor powered by Gemini Flash."""

    def __init__(self):
        self.config = get_ai_config()
        self.prompt_template = load_prompt("extract_cv.txt")

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
        """Estimate cumulative experience in years from work history dates."""
        total_months = 0
        current_year = datetime.now().year
        current_month = datetime.now().month

        for item in work_history:
            try:
                start_parts = [int(p) for p in re.findall(r"\d+", item.start_date)]
                if not start_parts:
                    continue
                start_y = start_parts[0]
                start_m = start_parts[1] if len(start_parts) > 1 else 1

                if item.is_current or not item.end_date:
                    end_y, end_m = current_year, current_month
                else:
                    end_parts = [int(p) for p in re.findall(r"\d+", item.end_date)]
                    if not end_parts:
                        continue
                    end_y = end_parts[0]
                    end_m = end_parts[1] if len(end_parts) > 1 else 12

                months = (end_y - start_y) * 12 + (end_m - start_m)
                if months > 0:
                    total_months += months
            except Exception:
                continue

        return round(total_months / 12.0, 1) if total_months > 0 else 0.0

    def _auto_heal_profile(self, data: dict) -> CandidateProfile:
        """Apply auto-healing transformations before Pydantic validation."""
        # Ensure personal_info exists
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
        """Extract structured CandidateProfile from raw text via Gemini Flash."""
        client = get_gemini_client()
        prompt = self.prompt_template.replace("{cv_text}", raw_text)

        response = client.models.generate_content(
            model=self.config.extraction_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=self.config.extraction_temperature,
                max_output_tokens=self.config.extraction_max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Gemini trả về phản hồi rỗng khi trích xuất CV.")

        try:
            raw_json_str = response.text.strip()
            if raw_json_str.startswith("```"):
                raw_json_str = re.sub(r"^```(?:json)?\n?", "", raw_json_str)
                raw_json_str = re.sub(r"\n?```$", "", raw_json_str)

            data = json.loads(raw_json_str)
            return self._auto_heal_profile(data)
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Không thể phân tích dữ liệu trích xuất từ CV: {e}")
