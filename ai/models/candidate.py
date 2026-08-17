"""Pydantic v2 Canonical Schemas for Candidate Profile (v3).

Designed for production-grade CV extraction across English and Vietnamese formats,
supporting 7 core sections, 8-group skills taxonomy, and dynamic additional sections.
"""

import math
from typing import Literal
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """Personal contact and identification details."""

    full_name: str = Field(description="Full legal or professional name of the candidate")
    email: str | None = Field(default=None, description="Email address")
    phone: str | None = Field(default=None, description="Phone number normalized")
    location: str | None = Field(default=None, description="City, Region, or Country")
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL")
    github_url: str | None = Field(default=None, description="GitHub profile URL")
    portfolio_url: str | None = Field(default=None, description="Personal website or portfolio URL")
    date_of_birth: str | None = Field(default=None, description="Date of birth if present (e.g. DD/MM/YYYY or YYYY-MM-DD)")


class SummarySection(BaseModel):
    """Professional summary / Objective / About Me."""

    summary_text: str | None = Field(default=None, description="Verbatim professional summary or objective")
    detected_title: str = Field(default="", description="Primary job title / headline extracted from header or summary")


class EducationItem(BaseModel):
    """Educational background entry."""

    institution: str = Field(description="University, College, or School name")
    degree: str = Field(default="", description="Degree type (e.g. Bachelor, Master, Engineer, Certificate)")
    field_of_study: str = Field(default="", description="Major / Specialization (e.g. Computer Science)")
    start_year: int | None = Field(default=None, description="Start year")
    end_year: int | None = Field(default=None, description="End/Graduation year (null if currently studying)")
    gpa: str | None = Field(default=None, description="GPA score as written (e.g. 3.6/4.0, 8.5/10)")


class WorkExperienceItem(BaseModel):
    """Work experience entry."""

    company: str = Field(description="Company or Organization name")
    role: str = Field(description="Job title / Role held")
    start_date: str = Field(default="", description="Start date (YYYY-MM or YYYY)")
    end_date: str | None = Field(default=None, description="End date (YYYY-MM, YYYY, or null if current/present)")
    is_current: bool = Field(default=False, description="True if currently working here")
    location: str | None = Field(default=None, description="Job location or Remote")
    raw_bullets: list[str] = Field(default_factory=list, description="Verbatim bullet points of responsibilities and achievements")


class ProjectItem(BaseModel):
    """Personal, Academic, or Freelance Project entry."""

    name: str = Field(description="Project title")
    description: str = Field(default="", description="Project summary description")
    role: str | None = Field(default=None, description="Role in project (e.g. Lead Developer, Contributor)")
    technologies: list[str] = Field(default_factory=list, description="Tech stack / Tools used in this project")
    url: str | None = Field(default=None, description="Project demo or repo link")
    highlights: list[str] = Field(default_factory=list, description="Bullet points detailing achievements/features")


class SkillsTaxonomy(BaseModel):
    """Standardized 8-group IT skills taxonomy (Flat lists of skill names)."""

    programming_languages: list[str] = Field(default_factory=list, description="Languages: Python, Go, TypeScript, Java, C++, etc.")
    frameworks: list[str] = Field(default_factory=list, description="Frameworks/Libs: FastAPI, React, Spring Boot, PyTorch, LangChain, etc.")
    databases: list[str] = Field(default_factory=list, description="DBs & Caches: PostgreSQL, MongoDB, Redis, MySQL, Qdrant, etc.")
    devops_and_cloud: list[str] = Field(default_factory=list, description="Infra & Cloud: Docker, Kubernetes, AWS, GCP, CI/CD, Terraform, etc.")
    ai_and_ml: list[str] = Field(default_factory=list, description="AI/ML: RAG, LLMs, Agentic AI, Computer Vision, NLP, Prompt Eng, etc.")
    testing: list[str] = Field(default_factory=list, description="Testing: pytest, Playwright, Jest, JUnit, Postman, etc.")
    tools: list[str] = Field(default_factory=list, description="Tools: Git, Linux, Jira, Docker Desktop, VS Code, Figma, etc.")
    soft_skills: list[str] = Field(default_factory=list, description="Soft skills: Leadership, Agile/Scrum, Communication, Problem Solving, etc.")


class CertificationItem(BaseModel):
    """Professional certification."""

    name: str = Field(description="Certification title (e.g. AWS Certified Solutions Architect)")
    issuer: str | None = Field(default=None, description="Issuing organization (e.g. Amazon, Google, Microsoft)")
    issue_date: str | None = Field(default=None, description="Date issued (YYYY-MM or YYYY)")
    credential_url: str | None = Field(default=None, description="Verification URL or Credential ID")


class LanguageItem(BaseModel):
    """Spoken / Written Language proficiency."""

    language: str = Field(description="Language name (e.g. English, Vietnamese, Japanese)")
    proficiency: str = Field(default="Professional", description="Proficiency level (e.g. Native, Fluent, IELTS 7.5, TOEIC 850, N2)")


class AdditionalSectionItem(BaseModel):
    """Dynamic custom sections found in CV (Awards, Volunteering, Publications, etc.)."""

    section_name: str = Field(description="Original section header name from CV")
    section_type: Literal["awards", "activities", "publications", "interests", "references", "other"] = Field(
        default="other", description="Standardized classification category"
    )
    items: list[str] = Field(default_factory=list, description="Extracted text items or bullets in this section")


class CVMetadata(BaseModel):
    """Calculated metadata and diagnostics for extraction quality."""

    total_experience_years: float = Field(default=0.0, description="Total years of work experience calculated from history")
    cv_language: Literal["en", "vi", "mixed"] = Field(default="en", description="Primary detected language of the CV")
    cv_format_type: Literal["chronological", "functional", "academic", "creative", "combination"] = Field(
        default="chronological", description="Detected CV layout format type"
    )
    has_clear_sections: bool = Field(default=True, description="Whether the CV has clearly labeled section headers")
    extraction_confidence: int = Field(default=95, description="Confidence score (0-100) of parsing completeness")
    detected_sections: list[str] = Field(default_factory=list, description="List of recognized sections from the document")


class CandidateProfile(BaseModel):
    """Canonical Candidate Profile (v3) - Single Source of Truth for AI pipeline."""

    personal_info: PersonalInfo
    summary: SummarySection = Field(default_factory=SummarySection)
    education: list[EducationItem] = Field(default_factory=list)
    work_experience: list[WorkExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    skills_taxonomy: SkillsTaxonomy = Field(default_factory=SkillsTaxonomy)
    certifications: list[CertificationItem] = Field(default_factory=list)
    languages: list[LanguageItem] = Field(default_factory=list)
    additional_sections: list[AdditionalSectionItem] = Field(default_factory=list)
    metadata: CVMetadata = Field(default_factory=CVMetadata)

    @property
    def full_name(self) -> str:
        return self.personal_info.full_name

    @property
    def email(self) -> str | None:
        return self.personal_info.email

    @property
    def title(self) -> str:
        return self.summary.detected_title or ""

    @property
    def experience_years(self) -> int:
        """Conservative integer years (never inflated)."""
        return math.floor(self.metadata.total_experience_years)
