"""Grounded one-page CV synthesis with provider-neutral execution."""

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
from ai.grounding import ground_cv_for_export
from ai.models.candidate import CandidateProfile
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardCertAndLangSection,
    HarvardContactInfo,
    HarvardEducationItem,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
)
from ai.models.jd import JDMatchReport, JDProfile
from ai.privacy import profile_payload_for_llm, sanitize_llm_input
from ai.prompts import load_composed_prompt


logger = logging.getLogger(__name__)


class HarvardCVSynthesizer:
    """Generate a tailored layout without sending contact PII to an LLM."""

    def __init__(
        self,
        ai_provider: Literal["openai", "gemini"] | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.ai_provider = ai_provider or self.config.ai_provider
        self.enable_fallback = self.config.enable_fallback if enable_fallback is None else enable_fallback
        self.system_instruction = load_composed_prompt("system_prompt.md", "synthesize_cv.md")
        self._executor = get_ai_executor()

    def _prepare_payload(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"] = "vi",
    ) -> str:
        payload = (
            f"<target_language>{target_language}</target_language>\n\n"
            f"<candidate_profile>{profile_payload_for_llm(profile)}</candidate_profile>\n\n"
            f"<job_description>{jd.model_dump_json()}</job_description>\n\n"
            f"<ats_match_report>{report.model_dump_json()}</ats_match_report>"
        )
        return sanitize_llm_input(payload)

    @staticmethod
    def _post_process_cv(cv: HarvardCVData, profile: CandidateProfile) -> HarvardCVData:
        all_skills = [skill for category in cv.skills_categories for skill in category.skills]
        if len(all_skills) > 15:
            remaining = 15
            categories: list[HarvardSkillsCategory] = []
            for category in cv.skills_categories:
                if remaining <= 0:
                    break
                selected = category.skills[:remaining]
                if selected:
                    categories.append(HarvardSkillsCategory(category_name=category.category_name, skills=selected))
                    remaining -= len(selected)
            cv.skills_categories = categories
        words = [
            cv.contact.full_name,
            cv.summary or "",
            *[f"{item.company} {item.role} {' '.join(item.bullets)}" for item in cv.experience],
            *[f"{item.name} {' '.join(item.bullets)}" for item in cv.projects],
            *[" ".join(item.skills) for item in cv.skills_categories],
        ]
        cv.estimated_word_count = len(" ".join(words).split())
        return cv

    async def _synthesize_with_openai(
        self, profile: CandidateProfile, jd: JDProfile, report: JDMatchReport, target_language: Literal["en", "vi"]
    ) -> HarvardCVData:
        completion = await get_openai_client().beta.chat.completions.parse(
            model=self.config.model_for("generation", "openai"),
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": self._prepare_payload(profile, jd, report, target_language)},
            ],
            response_format=HarvardCVData,
            temperature=self.config.reasoning_temperature,
            max_tokens=self.config.reasoning_max_tokens,
        )
        parsed = completion.choices[0].message.parsed
        if not parsed:
            raise ValueError("OpenAI returned no structured CV")
        return self._post_process_cv(parsed, profile)

    async def _synthesize_with_gemini(
        self, profile: CandidateProfile, jd: JDProfile, report: JDMatchReport, target_language: Literal["en", "vi"]
    ) -> HarvardCVData:
        response = await get_gemini_client().aio.models.generate_content(
            model=self.config.model_for("generation", "gemini"),
            contents=self._prepare_payload(profile, jd, report, target_language),
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=self.config.reasoning_temperature,
                response_mime_type="application/json",
                response_schema=HarvardCVData,
                max_output_tokens=self.config.reasoning_max_tokens,
            ),
        )
        raw = response.text or ""
        raw = re.sub(r"^```(?:json)?\n?|\n?```$", "", raw.strip())
        try:
            return self._post_process_cv(HarvardCVData.model_validate(json.loads(raw)), profile)
        except (json.JSONDecodeError, ValidationError) as error:
            raise ValueError("Gemini returned an invalid CV schema") from error

    def _synthesize_heuristic_fallback(
        self, profile: CandidateProfile, jd: JDProfile, report: JDMatchReport, target_language: Literal["en", "vi"]
    ) -> HarvardCVData:
        is_vi = target_language == "vi"
        target_title = jd.job_title or profile.title or ("Software Engineer" if not is_vi else "Kỹ sư phần mềm")
        cv = HarvardCVData(
            target_language=target_language,
            target_role=target_title,
            company_name=jd.company_name,
            contact=HarvardContactInfo(
                full_name=profile.personal_info.full_name,
                email=profile.personal_info.email,
                phone=profile.personal_info.phone,
                location=profile.personal_info.location,
                linkedin_url=profile.personal_info.linkedin_url,
                github_url=profile.personal_info.github_url,
            ),
            summary=(
                f"{target_title} with {profile.experience_years} years of documented experience."
                if not is_vi
                else f"Kỹ sư {target_title} với {profile.experience_years} năm kinh nghiệm được ghi nhận trong hồ sơ."
            ),
            education=[
                HarvardEducationItem(
                    institution=item.institution,
                    degree_major=" ".join(value for value in (item.degree, item.field_of_study) if value),
                    graduation_year=str(item.end_year or item.start_year or ""),
                    gpa_honors=f"GPA: {item.gpa}" if item.gpa else None,
                )
                for item in profile.education[:2]
            ],
            experience=[
                HarvardExperienceItem(
                    company=item.company,
                    role=item.role,
                    date_range=f"{item.start_date} - {item.end_date or ('Present' if not is_vi else 'Hiện tại')}",
                    location=item.location,
                    bullets=item.raw_bullets[:3],
                )
                for item in profile.work_experience[:3]
            ],
            projects=[
                HarvardProjectItem(
                    name=item.name,
                    role_or_tech=(f"{item.role or 'Developer'} | {', '.join(item.technologies[:4])}" if item.technologies else (item.role or "Developer")),
                    url=item.url,
                    bullets=item.highlights[:2] or ([item.description] if item.description else []),
                )
                for item in profile.projects[:2]
            ],
            skills_categories=[
                HarvardSkillsCategory(
                    category_name="Skills",
                    skills=[match.skill_name for match in report.matched_skills if match.skill_name][:15],
                )
            ],
            certifications_and_languages=HarvardCertAndLangSection(
                certifications=[item.name for item in profile.certifications],
                languages=[f"{item.language} ({item.proficiency})" for item in profile.languages],
            ),
            ats_score_estimate=report.overall_score,
        )
        return self._post_process_cv(cv, profile)

    async def synthesize(
        self, profile: CandidateProfile, jd: JDProfile, report: JDMatchReport, target_language: Literal["en", "vi"] = "vi"
    ) -> HarvardCVData:
        primary = self._synthesize_with_openai if self.ai_provider == "openai" else self._synthesize_with_gemini
        fallback = self._synthesize_with_gemini if self.ai_provider == "openai" else self._synthesize_with_openai
        try:
            result = await self._executor.run(
                stage=AIStage.GENERATION,
                primary_provider=self.ai_provider,
                primary=lambda: primary(profile, jd, report, target_language),
                fallback_provider=("gemini" if self.ai_provider == "openai" else "openai") if self.enable_fallback else None,
                fallback=(lambda: fallback(profile, jd, report, target_language)) if self.enable_fallback else None,
                input_chars=len(self._prepare_payload(profile, jd, report, target_language)),
                primary_model=self.config.model_for("generation", self.ai_provider),
                fallback_model=self.config.model_for("generation", "gemini" if self.ai_provider == "openai" else "openai"),
            )
            cv = result.value
            logger.info("CV synthesis completed trace_id=%s provider=%s", result.trace_id, result.provider)
        except Exception:
            logger.warning("CV synthesis unavailable; using deterministic source-backed fallback")
            cv = self._synthesize_heuristic_fallback(profile, jd, report, target_language)
        grounded, _ = ground_cv_for_export(cv, profile, report)
        return self._post_process_cv(grounded, profile)
