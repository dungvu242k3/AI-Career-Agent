"""Pydantic schemas for Candidate Profile — output of CV extraction."""

from pydantic import BaseModel


class SkillItem(BaseModel):
    name: str
    level: str = "intermediate"  # expert | intermediate | beginner
    category: str = "general"  # programming | framework | devops | database | soft_skill


class EducationItem(BaseModel):
    institution: str
    degree: str
    field: str = ""
    start_year: int | None = None
    end_year: int | None = None
    gpa: str | None = None


class WorkItem(BaseModel):
    company: str
    title: str
    start_date: str = ""
    end_date: str | None = None  # None = current
    location: str | None = None
    bullets: list[str] = []


class ProjectItem(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = []
    url: str | None = None


class CandidateProfile(BaseModel):
    """Standardized candidate profile extracted from CV."""

    # Personal info
    full_name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

    # Overview
    title: str = ""
    summary: str | None = None
    experience_years: int = 0

    # Details
    skills: list[SkillItem] = []
    education: list[EducationItem] = []
    work_history: list[WorkItem] = []
    projects: list[ProjectItem] = []
    certifications: list[str] = []

    # Goals
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []
    salary_expectation: str | None = None
