"""Pydantic schemas for CV Analysis Report — output of ATS scoring."""

from pydantic import BaseModel


class RubricItem(BaseModel):
    """Single scoring category in the ATS rubric."""

    category: str  # contact_info | professional_summary | skills_relevance | ...
    label: str  # Human-readable label
    score: int  # Actual score
    max_score: int  # Maximum possible score
    feedback: str  # Explanation


class BulletImprovement(BaseModel):
    """A CV bullet point that should be rewritten."""

    original: str
    improved: str
    reason: str
    star_score: int = 0  # 0-10, how well it follows STAR format


class Recommendation(BaseModel):
    """A specific improvement recommendation."""

    priority: str  # HIGH | MEDIUM | LOW
    category: str  # work_experience | skills | summary | formatting
    title: str
    description: str
    current: str | None = None  # Current text in CV
    suggested: str | None = None  # Suggested replacement


class AnalysisReport(BaseModel):
    """Complete CV analysis report with ATS scoring."""

    # Overall score
    ats_score: int  # 0-100
    ats_grade: str  # A+ | A | B+ | B | C+ | C | D | F

    # Detailed rubric (7 categories, total 100 points)
    rubric: list[RubricItem]

    # Skill analysis
    strong_skills: list[str]
    weak_skills: list[str]
    missing_for_market: list[str]  # Trending skills the CV lacks

    # Recommendations
    recommendations: list[Recommendation]

    # Bullet improvements
    bullets_to_improve: list[BulletImprovement]

    # Summary
    overall_feedback: str  # 2-3 sentence summary
