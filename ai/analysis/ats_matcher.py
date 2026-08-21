"""ATS scoring with source-minimised prompts and reliable provider execution."""

from __future__ import annotations

import json
import logging
import re
from typing import Literal

from google.genai import types
from pydantic import ValidationError

from ai.client import get_gemini_client, get_openai_client
from ai.config import get_ai_config
from ai.execution import AIStage, get_ai_executor
from ai.models.candidate import CandidateProfile
from ai.models.jd import JDMatchReport, JDProfile, WEIGHT_EXPERIENCE, WEIGHT_FORMAT, WEIGHT_SKILLS
from ai.privacy import profile_payload_for_llm, sanitize_llm_input
from ai.prompts import load_composed_prompt


logger = logging.getLogger(__name__)


class ATSMatcher:
    def __init__(
        self,
        ai_provider: Literal["openai", "gemini"] | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.ai_provider = ai_provider or self.config.ai_provider
        self.enable_fallback = self.config.enable_fallback if enable_fallback is None else enable_fallback
        self.system_instruction = load_composed_prompt("system_prompt.md", "ats_scoring.md")
        self._executor = get_ai_executor()

    def _prepare_payload(self, profile: CandidateProfile, jd: JDProfile) -> str:
        return sanitize_llm_input(
            f"<candidate_profile>{profile_payload_for_llm(profile)}</candidate_profile>\n"
            f"<target_job_description>{jd.model_dump_json()}</target_job_description>"
        )

    def _normalize_report(
        self, report: JDMatchReport, jd: JDProfile, profile: CandidateProfile | None = None
    ) -> JDMatchReport:
        report.skill_match_score = max(0, min(100, report.skill_match_score))
        report.experience_fit_score = max(0, min(100, report.experience_fit_score))
        report.format_quality_score = max(0, min(100, report.format_quality_score))
        if profile:
            total_skills = sum(
                len(items) for items in profile.skills_taxonomy.model_dump().values() if isinstance(items, list)
            )
            report.total_cv_skills_count = total_skills
            if total_skills > 25:
                report.skill_density_status = "bloated"
                report.format_quality_score = max(0, report.format_quality_score - 10)
                if not report.pruning_suggestions:
                    report.pruning_suggestions.append("Giảm kỹ năng không liên quan để hồ sơ tinh gọn và tập trung.")
            elif total_skills < 6:
                report.skill_density_status = "sparse"
            else:
                report.skill_density_status = "optimal"

        if report.matched_skills:
            proven = sum(1 for item in report.matched_skills if item.has_contextual_proof)
            report.verified_skills_ratio = round(proven / len(report.matched_skills), 2)
            if report.verified_skills_ratio < 0.6:
                factor = 0.70 + 0.30 * report.verified_skills_ratio
                report.skill_match_score = round(report.skill_match_score * factor)
        else:
            report.verified_skills_ratio = 1.0

        report.overall_score = max(
            0,
            min(
                100,
                round(
                    report.skill_match_score * WEIGHT_SKILLS
                    + report.experience_fit_score * WEIGHT_EXPERIENCE
                    + report.format_quality_score * WEIGHT_FORMAT
                ),
            ),
        )
        if not report.jd_title:
            report.jd_title = jd.job_title
        return report

    async def _match_with_openai(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        completion = await get_openai_client().beta.chat.completions.parse(
            model=self.config.model_for("analysis", "openai"),
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": self._prepare_payload(profile, jd)},
            ],
            response_format=JDMatchReport,
            temperature=self.config.reasoning_temperature,
            max_tokens=self.config.reasoning_max_tokens,
        )
        parsed = completion.choices[0].message.parsed
        if not parsed:
            raise ValueError("OpenAI returned no structured ATS report")
        return self._normalize_report(parsed, jd, profile)

    async def _match_with_gemini(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        response = await get_gemini_client().aio.models.generate_content(
            model=self.config.model_for("analysis", "gemini"),
            contents=self._prepare_payload(profile, jd),
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=JDMatchReport,
                temperature=self.config.reasoning_temperature,
                max_output_tokens=self.config.reasoning_max_tokens,
            ),
        )
        raw = re.sub(r"^```(?:json)?\n?|\n?```$", "", (response.text or "").strip())
        try:
            return self._normalize_report(JDMatchReport.model_validate(json.loads(raw)), jd, profile)
        except (json.JSONDecodeError, ValidationError) as error:
            raise ValueError("Gemini returned an invalid ATS schema") from error

    async def match(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        primary = self._match_with_openai if self.ai_provider == "openai" else self._match_with_gemini
        fallback = self._match_with_gemini if self.ai_provider == "openai" else self._match_with_openai
        payload_size = len(self._prepare_payload(profile, jd))
        outcome = await self._executor.run(
            stage=AIStage.ANALYSIS,
            primary_provider=self.ai_provider,
            primary=lambda: primary(profile, jd),
            fallback_provider=("gemini" if self.ai_provider == "openai" else "openai") if self.enable_fallback else None,
            fallback=(lambda: fallback(profile, jd)) if self.enable_fallback else None,
            input_chars=payload_size,
            primary_model=self.config.model_for("analysis", self.ai_provider),
            fallback_model=self.config.model_for("analysis", "gemini" if self.ai_provider == "openai" else "openai"),
        )
        logger.info("ATS matching completed trace_id=%s provider=%s", outcome.trace_id, outcome.provider)
        return outcome.value


def get_default_ats_matcher() -> ATSMatcher:
    return ATSMatcher()
