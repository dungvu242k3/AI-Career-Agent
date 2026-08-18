"""Canonical Pydantic v2 data models for Harvard 1-Page CV Synthesis.

Sections order:
1. Contact / Header
2. Professional Summary (Tailored, 2-3 lines)
3. Education
4. Work Experience (STAR-formatted bullet points)
5. Projects (Positioned above Technical Skills)
6. Technical Skills (10-15 core skills, anti-stuffing)
7. Certifications & Languages (Merged final section)
"""

from typing import Literal
from pydantic import BaseModel, Field


class HarvardContactInfo(BaseModel):
    """Personal contact details formatted for single-line Harvard header."""

    full_name: str = Field(description="Candidate's full legal/professional name")
    email: str | None = Field(default=None, description="Professional email address")
    phone: str | None = Field(default=None, description="Formatted phone number")
    location: str | None = Field(default=None, description="City, Country (e.g. Hanoi, Vietnam)")
    linkedin_url: str | None = Field(default=None, description="LinkedIn handle or URL")
    github_url: str | None = Field(default=None, description="GitHub URL or portfolio link")


class HarvardEducationItem(BaseModel):
    """Education entry formatted for Harvard template."""

    institution: str = Field(description="University / College / School name")
    degree_major: str = Field(description="Degree and Major (e.g. Bachelor of Science in Computer Science)")
    graduation_year: str = Field(description="Graduation year or date range (e.g. 2020 - 2024 or 2024)")
    gpa_honors: str | None = Field(default=None, description="GPA or academic honors if present (e.g. GPA 3.7/4.0, Top 5%)")


class HarvardExperienceItem(BaseModel):
    """Work experience entry formatted with STAR bullet points."""

    company: str = Field(description="Company or Organization name")
    role: str = Field(description="Job Title / Role held")
    date_range: str = Field(description="Employment duration (e.g. 06/2022 - Present or 2022 - 2024)")
    location: str | None = Field(default=None, description="Job Location (e.g. Ho Chi Minh City, Vietnam or Remote)")
    bullets: list[str] = Field(
        default_factory=list,
        description="2-4 high-impact STAR bullet points starting with strong action verbs and measurable metrics",
    )


class HarvardProjectItem(BaseModel):
    """Project entry positioned before skills to showcase practical experience."""

    name: str = Field(description="Project name / Title")
    role_or_tech: str = Field(description="Role or Core Tech Stack (e.g. Lead Engineer | FastAPI, Docker, PostgreSQL)")
    date_range: str | None = Field(default=None, description="Project timeline if applicable")
    url: str | None = Field(default=None, description="Live URL or repository link if present")
    bullets: list[str] = Field(
        default_factory=list,
        description="1-3 concise bullet points detailing architecture, implementation, and impact",
    )


class HarvardSkillsCategory(BaseModel):
    """Categorized technical skills (strictly 10-15 skills total)."""

    category_name: str = Field(description="Category label (e.g. Languages & Frameworks, Cloud & Databases, Tools)")
    skills: list[str] = Field(default_factory=list, description="List of specific skill names")


class HarvardCertAndLangSection(BaseModel):
    """Merged Certifications & Languages section at the bottom of the CV."""

    certifications: list[str] = Field(default_factory=list, description="List of professional certifications")
    languages: list[str] = Field(default_factory=list, description="Languages and proficiencies (e.g. English (Fluent - IELTS 7.5))")


class HarvardCVData(BaseModel):
    """Complete Canonical Data Structure for 1-Page Harvard CV."""

    target_language: Literal["en", "vi"] = Field(default="vi", description="Target language of the CV")
    target_role: str = Field(description="Target Job Title tailored for")
    company_name: str | None = Field(default=None, description="Target company name if applicable")

    contact: HarvardContactInfo
    summary: str | None = Field(
        default=None,
        description="Concise, 2-3 sentence tailored executive summary highlighting core value proposition",
    )
    education: list[HarvardEducationItem] = Field(default_factory=list)
    experience: list[HarvardExperienceItem] = Field(default_factory=list)
    projects: list[HarvardProjectItem] = Field(default_factory=list)
    skills_categories: list[HarvardSkillsCategory] = Field(default_factory=list)
    certifications_and_languages: HarvardCertAndLangSection = Field(default_factory=HarvardCertAndLangSection)

    estimated_word_count: int = Field(default=0, description="Approximate total word count to ensure 1-page fit")
    ats_score_estimate: int = Field(default=85, description="Estimated ATS match score for this tailored CV")
