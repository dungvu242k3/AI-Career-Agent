"""ATS Matching Engine — 3-pillar scoring (Skills 50% + Experience 30% + Format 20%) with multi-provider LLM fallback."""

import json
import logging
import re
from typing import Literal
from google.genai import types
from pydantic import ValidationError

from ai.config import get_ai_config
from ai.client import get_openai_client, get_gemini_client
from ai.models.candidate import CandidateProfile
from ai.models.jd import (
    JDProfile,
    JDMatchReport,
    WEIGHT_SKILLS,
    WEIGHT_EXPERIENCE,
    WEIGHT_FORMAT,
)
from ai.prompts import load_composed_prompt

logger = logging.getLogger(__name__)


class ATSMatcher:
    """Production ATS Scoring Engine comparing CandidateProfile against JDProfile."""

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

        self.system_instruction = load_composed_prompt(
            "system_prompt.md",
            "ats_scoring.md",
        )

    def _prepare_payload(self, profile: CandidateProfile, jd: JDProfile) -> str:
        """Format candidate profile and JD into structured prompt payload."""
        return (
            f"<candidate_profile>\n{profile.model_dump_json(indent=2)}\n</candidate_profile>\n\n"
            f"<target_job_description>\n{jd.model_dump_json(indent=2)}\n</target_job_description>"
        )

    def _normalize_report(
        self,
        report: JDMatchReport,
        jd: JDProfile,
        profile: CandidateProfile | None = None,
    ) -> JDMatchReport:
        """Ensure mathematical consistency, contextual proof weighting, and 10-15 skills anti-stuffing checks."""
        report.skill_match_score = max(0, min(100, report.skill_match_score))
        report.experience_fit_score = max(0, min(100, report.experience_fit_score))
        report.format_quality_score = max(0, min(100, report.format_quality_score))

        # 1. Calculate CV Skills Count and Density Status (10-15 Elite Standard)
        if profile:
            total_skills = sum(
                len(list_skills)
                for list_skills in profile.skills_taxonomy.model_dump().values()
                if isinstance(list_skills, list)
            )
            report.total_cv_skills_count = total_skills

            # Check for Skill Bloating / Stuffing (>25 skills)
            if total_skills > 25:
                report.skill_density_status = "bloated"
                # Penalize format score for bloated keyword stuffing
                report.format_quality_score = max(0, report.format_quality_score - 10)
                if not report.pruning_suggestions:
                    report.pruning_suggestions.append(
                        f"Hồ sơ đang liệt kê {total_skills} kỹ năng (vượt quá chuẩn 10-15 kỹ năng tinh gọn). "
                        "Hãy ẩn bớt các kỹ năng phụ hoặc không liên quan đến vị trí mục tiêu để làm nổi bật kỹ năng cốt lõi."
                    )
            elif total_skills < 6:
                report.skill_density_status = "sparse"
            else:
                report.skill_density_status = "optimal"

        # 2. Contextual Proof Ratio (Proven vs Listed-only)
        matched_items = report.matched_skills
        if matched_items:
            proven_count = sum(1 for m in matched_items if m.has_contextual_proof)
            report.verified_skills_ratio = round(proven_count / len(matched_items), 2)

            # If less than 60% of matched skills have proof in work experience, scale skill score
            if report.verified_skills_ratio < 0.6:
                penalty_factor = 0.70 + 0.30 * report.verified_skills_ratio
                report.skill_match_score = max(0, min(100, round(report.skill_match_score * penalty_factor)))
        else:
            report.verified_skills_ratio = 1.0

        # 3. Re-compute weighted overall score deterministically
        calculated_overall = round(
            report.skill_match_score * WEIGHT_SKILLS
            + report.experience_fit_score * WEIGHT_EXPERIENCE
            + report.format_quality_score * WEIGHT_FORMAT
        )
        report.overall_score = max(0, min(100, calculated_overall))

        if not report.jd_title:
            report.jd_title = jd.job_title

        return report

    async def _match_with_openai(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        """Match CV against JD via OpenAI Structured Outputs (gpt-4o)."""
        client = get_openai_client()
        user_content = self._prepare_payload(profile, jd)

        completion = await client.beta.chat.completions.parse(
            model=self.config.openai_reasoning_model,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": user_content},
            ],
            response_format=JDMatchReport,
            temperature=self.config.reasoning_temperature,
            max_tokens=self.config.reasoning_max_tokens,
        )

        parsed_report = completion.choices[0].message.parsed
        if not parsed_report:
            refusal = getattr(completion.choices[0].message, "refusal", None)
            if refusal:
                raise ValueError(f"OpenAI từ chối đánh giá ATS: {refusal}")
            raise ValueError("OpenAI trả về phản hồi rỗng khi đánh giá ATS.")

        return self._normalize_report(parsed_report, jd, profile=profile)

    async def _match_with_gemini(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        """Match CV against JD via Google Gemini response schema."""
        client = get_gemini_client()
        user_content = self._prepare_payload(profile, jd)

        response = await client.aio.models.generate_content(
            model=self.config.gemini_flash_model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=JDMatchReport,
                temperature=self.config.reasoning_temperature,
                max_output_tokens=self.config.reasoning_max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Gemini trả về phản hồi rỗng khi đánh giá ATS.")

        raw_json_str = response.text.strip()
        if raw_json_str.startswith("```"):
            raw_json_str = re.sub(r"^```(?:json)?\n?", "", raw_json_str)
            raw_json_str = re.sub(r"\n?```$", "", raw_json_str)

        try:
            data = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI trả về định dạng JSON không hợp lệ: {e}")

        try:
            report = JDMatchReport.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Dữ liệu báo cáo ATS không đúng cấu trúc quy định: {e}")

        return self._normalize_report(report, jd, profile=profile)

    async def match(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        """Execute end-to-end ATS matching with automatic multi-provider fallback."""
        primary_fn = (
            self._match_with_openai
            if self.ai_provider == "openai"
            else self._match_with_gemini
        )
        fallback_fn = (
            self._match_with_gemini
            if self.ai_provider == "openai"
            else self._match_with_openai
        )

        try:
            return await primary_fn(profile, jd)
        except Exception as primary_err:
            if not self.enable_fallback:
                logger.error("Primary ATS matching failed: %s", primary_err)
                raise

            logger.warning(
                "Primary ATS matcher failed: %s. Initiating secondary fallback...",
                primary_err,
            )
            try:
                report = await fallback_fn(profile, jd)
                logger.info("Secondary ATS matcher fallback succeeded.")
                return report
            except Exception as fallback_err:
                logger.error("Both primary and fallback ATS matchers failed: %s", fallback_err)
                raise ValueError(
                    f"Đánh giá ATS thất bại trên cả 2 nhà cung cấp AI: {primary_err} | {fallback_err}"
                )


def get_default_ats_matcher() -> ATSMatcher:
    """Factory function for default ATSMatcher instance."""
    return ATSMatcher()
