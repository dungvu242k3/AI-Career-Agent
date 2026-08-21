"""Deterministic source-grounding for generated career content.

An omitted claim is safer than an attractive but unverifiable one. This runs
immediately before CV data is rendered as a downloadable document.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

from ai.models.candidate import CandidateProfile
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardCertAndLangSection,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
)
from ai.models.jd import JDMatchReport


@dataclass
class GroundingReport:
    dropped_claims: list[str] = field(default_factory=list)
    verified_skills: int = 0
    verified_certifications: int = 0

    @property
    def is_grounded(self) -> bool:
        return not self.dropped_claims


def _normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _source_skills(profile: CandidateProfile) -> set[str]:
    return {
        _normalized(skill)
        for values in profile.skills_taxonomy.model_dump().values()
        if isinstance(values, list)
        for skill in values
        if isinstance(skill, str) and skill.strip()
    }


def ground_cv_for_export(
    cv: HarvardCVData,
    profile: CandidateProfile,
    ats_report: JDMatchReport,
) -> tuple[HarvardCVData, GroundingReport]:
    """Replace unverifiable model output with source-backed CV values."""
    diagnostics = GroundingReport()

    # Contact stays application-local until after the model call.
    cv.contact.full_name = profile.personal_info.full_name
    cv.contact.email = profile.personal_info.email
    cv.contact.phone = profile.personal_info.phone
    cv.contact.location = profile.personal_info.location
    cv.contact.linkedin_url = profile.personal_info.linkedin_url
    cv.contact.github_url = profile.personal_info.github_url

    title = profile.title or cv.target_role
    years = profile.experience_years
    cv.summary = (
        f"{title} with {years} years of documented experience."
        if cv.target_language == "en"
        else f"{title} với {years} năm kinh nghiệm được ghi nhận trong hồ sơ."
    )

    source_experience = {
        (_normalized(item.company), _normalized(item.role)): item
        for item in profile.work_experience
    }
    grounded_experience: list[HarvardExperienceItem] = []
    for item in cv.experience:
        source = source_experience.get((_normalized(item.company), _normalized(item.role)))
        if not source:
            diagnostics.dropped_claims.append(f"experience:{item.company}/{item.role}")
            continue
        grounded_experience.append(
            HarvardExperienceItem(
                company=source.company,
                role=source.role,
                date_range=f"{source.start_date} - {source.end_date or ('Present' if cv.target_language == 'en' else 'Hiện tại')}",
                location=source.location,
                bullets=source.raw_bullets[:3],
            )
        )
    cv.experience = grounded_experience

    source_projects = {_normalized(item.name): item for item in profile.projects}
    grounded_projects: list[HarvardProjectItem] = []
    for item in cv.projects:
        source = source_projects.get(_normalized(item.name))
        if not source:
            diagnostics.dropped_claims.append(f"project:{item.name}")
            continue
        grounded_projects.append(
            HarvardProjectItem(
                name=source.name,
                role_or_tech=(
                    f"{source.role or 'Developer'} | {', '.join(source.technologies[:4])}"
                    if source.technologies
                    else (source.role or "Developer")
                ),
                url=source.url,
                bullets=source.highlights[:2] or ([source.description] if source.description else []),
            )
        )
    cv.projects = grounded_projects

    known_skills = _source_skills(profile)
    grounded_categories: list[HarvardSkillsCategory] = []
    for category in cv.skills_categories:
        verified = [skill for skill in category.skills if _normalized(skill) in known_skills]
        for skill in category.skills:
            if _normalized(skill) not in known_skills:
                diagnostics.dropped_claims.append(f"skill:{skill}")
        if verified:
            diagnostics.verified_skills += len(verified)
            grounded_categories.append(HarvardSkillsCategory(category_name=category.category_name, skills=verified))
    cv.skills_categories = grounded_categories

    known_certs = {_normalized(cert.name): cert.name for cert in profile.certifications}
    kept_certs = []
    for cert in cv.certifications_and_languages.certifications:
        original = known_certs.get(_normalized(cert))
        if original:
            kept_certs.append(original)
            diagnostics.verified_certifications += 1
        else:
            diagnostics.dropped_claims.append(f"certification:{cert}")
    cv.certifications_and_languages = HarvardCertAndLangSection(
        certifications=kept_certs,
        languages=[f"{item.language} ({item.proficiency})" for item in profile.languages],
    )

    # Critic quality remains diagnostics. ATS is calculated by ATSMatcher.
    cv.ats_score_estimate = ats_report.overall_score
    return cv, diagnostics
