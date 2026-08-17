"""Canonical domain schemas for ATS scoring, rubric, and recommendations."""

from pydantic import BaseModel, Field


class RubricItem(BaseModel):
    category: str
    label: str
    score: int
    max_score: int
    feedback: str


class BulletImprovement(BaseModel):
    original: str
    improved: str
    reason: str
    star_score: int = 0


class Recommendation(BaseModel):
    priority: str  # HIGH | MEDIUM | LOW
    category: str
    title: str
    description: str
    current: str | None = None
    suggested: str | None = None


class AnalysisReport(BaseModel):
    ats_score: int
    ats_grade: str
    rubric: list[RubricItem] = Field(default_factory=list)
    strong_skills: list[str] = Field(default_factory=list)
    weak_skills: list[str] = Field(default_factory=list)
    missing_for_market: list[str] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    bullets_to_improve: list[BulletImprovement] = Field(default_factory=list)
    overall_feedback: str = ""
