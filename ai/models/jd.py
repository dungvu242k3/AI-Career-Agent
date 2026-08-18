"""Canonical domain schemas for Job Description parsing and ATS matching.

Production-grade Pydantic v2 models supporting:
- JD structured extraction (must-have vs nice-to-have skills)
- 3-layer ATS scoring (Skills 50% + Experience 30% + Format 20%)
- Skill-level match classification (exact / semantic / missing)
"""

from typing import Literal
from pydantic import BaseModel, Field, computed_field

# --- Grade mapping constants ---
GRADE_THRESHOLDS: list[tuple[int, str, str]] = [
    (90, "A+", "Rất phù hợp — Nên ứng tuyển ngay!"),
    (80, "A", "Phù hợp tốt — Cần bổ sung nhỏ"),
    (70, "B+", "Khá phù hợp — Cần cải thiện một số kỹ năng"),
    (60, "B", "Phù hợp trung bình — Cần nỗ lực bổ sung"),
    (0, "C", "Chưa phù hợp — Cần cải thiện đáng kể"),
]

# --- ATS weight constants (international standard) ---
WEIGHT_SKILLS = 0.50
WEIGHT_EXPERIENCE = 0.30
WEIGHT_FORMAT = 0.20


def compute_grade(score: int) -> tuple[str, str]:
    """Map numeric score (0-100) to letter grade and Vietnamese verdict."""
    for threshold, grade, verdict in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade, verdict
    return "C", GRADE_THRESHOLDS[-1][2]


# ──────────────────────────────────────────────
# JD Profile (Input: Parsed Job Description)
# ──────────────────────────────────────────────

class JDProfile(BaseModel):
    """Structured representation of a parsed Job Description."""

    job_title: str = Field(description="Target position title (e.g. Senior Backend Engineer)")
    company_name: str | None = Field(default=None, description="Hiring company name if present")

    must_have_skills: list[str] = Field(
        default_factory=list,
        description="Required skills explicitly stated as mandatory in JD",
    )
    nice_to_have_skills: list[str] = Field(
        default_factory=list,
        description="Preferred/bonus skills mentioned as advantageous",
    )

    min_experience_years: int | None = Field(
        default=None, ge=0, le=50,
        description="Minimum years of experience required",
    )
    education_requirement: str | None = Field(
        default=None,
        description="Education level requirement (e.g. Bachelor in CS)",
    )

    responsibilities: list[str] = Field(
        default_factory=list,
        description="Key job responsibilities extracted from JD",
    )
    benefits: list[str] = Field(
        default_factory=list,
        description="Company benefits and perks (optional)",
    )

    raw_text: str = Field(description="Original full JD text for reference")
    language: Literal["en", "vi", "mixed"] = Field(
        default="en",
        description="Detected primary language of the JD",
    )


# ──────────────────────────────────────────────
# Skill Match Item (Sub-model for match detail)
# ──────────────────────────────────────────────

class SkillMatchItem(BaseModel):
    """Individual skill comparison result between CV and JD."""

    skill_name: str = Field(description="Skill name from JD requirement")
    match_type: Literal["exact", "semantic", "missing"] = Field(
        description="Match classification: exact(🟢), semantic(🟡), missing(🔴)",
    )
    cv_evidence: str | None = Field(
        default=None,
        description="Evidence text found in CV (null if missing)",
    )
    jd_requirement: str = Field(
        description="Original requirement context from JD",
    )
    importance: Literal["required", "preferred"] = Field(
        description="Skill priority: required(must-have) or preferred(nice-to-have)",
    )
    has_contextual_proof: bool = Field(
        default=True,
        description="True if skill is proven with project or work experience bullet points",
    )
    recency_tier: Literal["recent", "legacy", "unspecified"] = Field(
        default="recent",
        description="Recency tier: recent (1-2 yrs), legacy (past), unspecified",
    )
    proof_snippet: str | None = Field(
        default=None,
        description="Excerpt from work experience or project proving this skill",
    )


# ──────────────────────────────────────────────
# JD Match Report (Output: Full ATS Analysis)
# ──────────────────────────────────────────────

class JDMatchReport(BaseModel):
    """Complete ATS match analysis report — all user-facing text in Vietnamese."""

    # Overall scoring
    overall_score: int = Field(ge=0, le=100, description="Weighted total: Skills×50% + Exp×30% + Format×20%")

    # 3-pillar sub-scores
    skill_match_score: int = Field(ge=0, le=100, description="Keyword and semantic skill match score")
    experience_fit_score: int = Field(ge=0, le=100, description="Years of experience and depth fit score")
    format_quality_score: int = Field(ge=0, le=100, description="CV format, STAR structure, metrics usage score")

    # Skill depth & anti-stuffing metrics
    skill_density_status: Literal["optimal", "bloated", "sparse"] = Field(
        default="optimal",
        description="Skill density: optimal (10-15), bloated (>25), sparse (<6)",
    )
    total_cv_skills_count: int = Field(
        default=0,
        description="Total count of skills found on CV",
    )
    verified_skills_ratio: float = Field(
        default=1.0,
        description="Ratio of matched skills backed by contextual proof (0.0 to 1.0)",
    )
    pruning_suggestions: list[str] = Field(
        default_factory=list,
        description="Advice on removing irrelevant/bloated skills to sharpen CV focus (Vietnamese)",
    )

    # Skill breakdown
    matched_skills: list[SkillMatchItem] = Field(
        default_factory=list,
        description="Skills with exact(🟢) or semantic(🟡) match",
    )
    missing_skills: list[SkillMatchItem] = Field(
        default_factory=list,
        description="Skills missing from CV(🔴) — clickable for STAR generation",
    )
    excess_skills: list[str] = Field(
        default_factory=list,
        description="CV skills not relevant to this JD(⚪)",
    )

    # Actionable insights (Vietnamese)
    top_recommendations: list[str] = Field(
        default_factory=list,
        description="Top 3 specific actions to increase ATS score (Vietnamese)",
    )
    experience_gap_analysis: str = Field(
        default="",
        description="Detailed experience gap analysis text (Vietnamese)",
    )

    # Metadata
    jd_title: str = Field(default="", description="Target job title from JD")
    analysis_language: Literal["vi"] = Field(default="vi", description="Report language — always Vietnamese")

    @computed_field
    @property
    def overall_grade(self) -> str:
        """Letter grade derived from overall_score."""
        grade, _ = compute_grade(self.overall_score)
        return grade

    @computed_field
    @property
    def verdict(self) -> str:
        """Vietnamese verdict derived from overall_score."""
        _, verdict = compute_grade(self.overall_score)
        return verdict
