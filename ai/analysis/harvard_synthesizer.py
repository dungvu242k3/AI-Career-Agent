"""Harvard 1-Page CV Synthesis Engine with multi-provider LLM fallback and anti-fabrication controls."""

import json
import logging
import re
from typing import Literal
from google.genai import types
from pydantic import ValidationError

from ai.config import get_ai_config
from ai.client import get_openai_client, get_gemini_client
from ai.models.candidate import CandidateProfile
from ai.models.jd import JDProfile, JDMatchReport
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardContactInfo,
    HarvardEducationItem,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
    HarvardCertAndLangSection,
)
from ai.prompts import load_composed_prompt

logger = logging.getLogger(__name__)


class HarvardCVSynthesizer:
    """Production AI Synthesis Engine compiling CandidateProfile + JD into a 1-page Harvard CV."""

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
            "synthesize_cv.md",
        )

    def _prepare_payload(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"] = "vi",
    ) -> str:
        """Format candidate profile, JD, and ATS report into structured XML prompt payload."""
        return (
            f"<target_language>{target_language}</target_language>\n\n"
            f"<candidate_profile>\n{profile.model_dump_json(indent=2)}\n</candidate_profile>\n\n"
            f"<job_description>\n{jd.model_dump_json(indent=2)}\n</job_description>\n\n"
            f"<ats_match_report>\n{report.model_dump_json(indent=2)}\n</ats_match_report>"
        )

    def _post_process_cv(self, cv: HarvardCVData, profile: CandidateProfile) -> HarvardCVData:
        """Enforce strict constraints (10-15 skills limit, word count estimation)."""
        # Count total skills across categories
        all_skills: list[str] = []
        for cat in cv.skills_categories:
            all_skills.extend(cat.skills)

        # Cap total skills to 15 if AI returned more
        if len(all_skills) > 15:
            logger.warning("Capping synthesized CV skills from %d to 15", len(all_skills))
            remaining = 15
            new_categories: list[HarvardSkillsCategory] = []
            for cat in cv.skills_categories:
                if remaining <= 0:
                    break
                take = min(len(cat.skills), remaining)
                new_categories.append(
                    HarvardSkillsCategory(
                        category_name=cat.category_name,
                        skills=cat.skills[:take],
                    )
                )
                remaining -= take
            cv.skills_categories = new_categories

        # Calculate estimated word count
        words: list[str] = [cv.contact.full_name]
        if cv.summary:
            words.extend(cv.summary.split())
        for edu in cv.education:
            words.extend(f"{edu.institution} {edu.degree_major} {edu.graduation_year}".split())
        for exp in cv.experience:
            words.extend(f"{exp.company} {exp.role} {exp.date_range}".split())
            for b in exp.bullets:
                words.extend(b.split())
        for proj in cv.projects:
            words.extend(f"{proj.name} {proj.role_or_tech}".split())
            for b in proj.bullets:
                words.extend(b.split())
        for cat in cv.skills_categories:
            words.extend(cat.category_name.split())
            for s in cat.skills:
                words.extend(s.split())
        for cert in cv.certifications_and_languages.certifications:
            words.extend(cert.split())
        for lang in cv.certifications_and_languages.languages:
            words.extend(lang.split())

        cv.estimated_word_count = len(words)
        return cv

    async def _synthesize_with_openai(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"],
    ) -> HarvardCVData:
        """Synthesize Harvard CV via OpenAI Structured Outputs."""
        client = get_openai_client()
        user_content = self._prepare_payload(profile, jd, report, target_language)

        response = await client.beta.chat.completions.parse(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": user_content},
            ],
            response_format=HarvardCVData,
            temperature=0.2,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("OpenAI returned empty structured response for Harvard CV synthesis")
        return self._post_process_cv(parsed, profile)

    async def _synthesize_with_gemini(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"],
    ) -> HarvardCVData:
        """Synthesize Harvard CV via Google Gemini SDK."""
        client = get_gemini_client()
        user_content = self._prepare_payload(profile, jd, report, target_language)

        response = await client.aio.models.generate_content(
            model=self.config.gemini_model,
            contents=[user_content],
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=HarvardCVData,
            ),
        )

        response_text = response.text or ""
        try:
            parsed = HarvardCVData.model_validate_json(response_text)
            return self._post_process_cv(parsed, profile)
        except ValidationError:
            # Fallback JSON regex extraction
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                parsed = HarvardCVData.model_validate(data)
                return self._post_process_cv(parsed, profile)
            raise

    def _synthesize_heuristic_fallback(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"],
    ) -> HarvardCVData:
        """Deterministic, zero-cost fallback guaranteeing a valid Harvard CV without LLM calls."""
        is_vi = target_language == "vi"

        # 1. Contact
        contact = HarvardContactInfo(
            full_name=profile.personal_info.full_name,
            email=profile.personal_info.email,
            phone=profile.personal_info.phone,
            location=profile.personal_info.location or ("Hà Nội, Việt Nam" if is_vi else "Hanoi, Vietnam"),
            linkedin_url=profile.personal_info.linkedin_url,
            github_url=profile.personal_info.github_url,
        )

        # 2. Summary
        target_title = jd.job_title or profile.title or ("Kỹ sư phần mềm" if is_vi else "Software Engineer")
        summary = (
            f"Kỹ sư {target_title} với hơn {profile.experience_years} năm kinh nghiệm thực chiến. "
            f"Thế mạnh chuyên sâu về thiết kế hệ thống, tối ưu hiệu năng và giải quyết bài toán kỹ thuật phức tạp."
            if is_vi
            else f"{target_title} with {profile.experience_years}+ years of proven engineering experience. "
            f"Specialized in system architecture, performance optimization, and scalable solution delivery."
        )

        # 3. Education
        education = [
            HarvardEducationItem(
                institution=edu.institution,
                degree_major=f"{edu.degree} in {edu.field_of_study}".strip(" in "),
                graduation_year=str(edu.end_year or edu.start_year or "2024"),
                gpa_honors=f"GPA: {edu.gpa}" if edu.gpa else None,
            )
            for edu in profile.education[:2]
        ]

        # 4. Experience
        if not profile.work_experience:
            logger.info("Candidate profile %s has empty work experience; generating academic/project-focused CV", profile.personal_info.full_name)

        experience = [
            HarvardExperienceItem(
                company=exp.company,
                role=exp.role,
                date_range=f"{exp.start_date} - {exp.end_date or ('Hiện tại' if is_vi else 'Present')}",
                location=exp.location,
                bullets=exp.raw_bullets[:3] if exp.raw_bullets else [
                    f"Phát triển và vận hành hệ thống phần mềm tại {exp.company}"
                    if is_vi
                    else f"Developed and maintained software systems at {exp.company}"
                ],
            )
            for exp in profile.work_experience[:3]
        ]

        # 5. Projects (Positioned before skills)
        if not profile.projects:
            logger.info("Candidate profile %s has no explicit projects; omitting projects section", profile.personal_info.full_name)

        projects = [
            HarvardProjectItem(
                name=proj.name,
                role_or_tech=f"{proj.role or 'Core Developer'} | {', '.join(proj.technologies[:4])}"
                if proj.technologies
                else (proj.role or "Developer"),
                date_range=None,
                url=proj.url,
                bullets=proj.highlights[:2] if proj.highlights else [proj.description] if proj.description else [],
            )
            for proj in profile.projects[:2]
        ]

        # 6. Skills (strictly 10-15 core skills)
        flat_skills: list[str] = []
        for match in report.matched_skills:
            if match.match_type in ("exact", "semantic") and match.skill_name not in flat_skills:
                flat_skills.append(match.skill_name)
        if len(flat_skills) < 10:
            # Backfill from profile taxonomy
            tax = profile.skills_taxonomy
            for pool in [
                tax.programming_languages,
                tax.frameworks,
                tax.databases,
                tax.devops_and_cloud,
                tax.ai_and_ml,
                tax.tools,
            ]:
                for s in pool:
                    if s not in flat_skills:
                        flat_skills.append(s)
                    if len(flat_skills) >= 15:
                        break
                if len(flat_skills) >= 15:
                    break

        selected_skills = flat_skills[:15]
        midpoint = max(1, len(selected_skills) // 2)
        skills_categories = [
            HarvardSkillsCategory(
                category_name="Languages & Frameworks" if not is_vi else "Ngôn ngữ & Frameworks",
                skills=selected_skills[:midpoint],
            ),
            HarvardSkillsCategory(
                category_name="Cloud, Databases & Tools" if not is_vi else "Cloud, Cơ sở dữ liệu & Công cụ",
                skills=selected_skills[midpoint:],
            ),
        ]

        # 7. Certifications & Languages
        certs = [c.name for c in profile.certifications]
        langs = [f"{l.language} ({l.proficiency})" for l in profile.languages]
        cert_and_lang = HarvardCertAndLangSection(
            certifications=certs,
            languages=langs,
        )

        cv_data = HarvardCVData(
            target_language=target_language,
            target_role=target_title,
            company_name=jd.company_name,
            contact=contact,
            summary=summary,
            education=education,
            experience=experience,
            projects=projects,
            skills_categories=skills_categories,
            certifications_and_languages=cert_and_lang,
            ats_score_estimate=report.overall_score,
        )
        return self._post_process_cv(cv_data, profile)

    async def synthesize(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"] = "vi",
    ) -> HarvardCVData:
        """Synthesize Harvard CV with primary provider and automatic fallback."""
        primary_provider = self.ai_provider
        fallback_provider: Literal["openai", "gemini"] = (
            "gemini" if primary_provider == "openai" else "openai"
        )

        try:
            if primary_provider == "openai":
                return await self._synthesize_with_openai(profile, jd, report, target_language)
            return await self._synthesize_with_gemini(profile, jd, report, target_language)
        except Exception as primary_err:
            logger.warning(
                "Primary provider %s failed for Harvard CV synthesis: %s",
                primary_provider,
                primary_err,
            )
            if not self.enable_fallback:
                logger.info("Fallback disabled. Using heuristic fallback.")
                return self._synthesize_heuristic_fallback(profile, jd, report, target_language)

            try:
                logger.info("Attempting fallback with %s...", fallback_provider)
                if fallback_provider == "openai":
                    return await self._synthesize_with_openai(profile, jd, report, target_language)
                return await self._synthesize_with_gemini(profile, jd, report, target_language)
            except Exception as fallback_err:
                logger.error(
                    "Fallback provider %s also failed for Harvard CV synthesis: %s. Using heuristic.",
                    fallback_provider,
                    fallback_err,
                )
                return self._synthesize_heuristic_fallback(profile, jd, report, target_language)
