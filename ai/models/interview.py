"""Canonical Pydantic models for Adversarial Multi-Agent Mock Interview Arena."""

from typing import Literal
from pydantic import BaseModel, Field


class InterviewerPersona(BaseModel):
    """Profile of an AI interviewer in the arena."""

    name: str = Field(description="Interviewer name: Alex or Sarah")
    role: str = Field(description="Title/Role: Tech Lead, HR Manager")
    avatar_color: str = Field(default="#10b981", description="Theme color")
    style: str = Field(description="Persona description: Sharp, Direct, Empathetic, Challenging")


class QuestionItem(BaseModel):
    """Interview question generated dynamically based on CV & JD."""

    id: str = Field(description="Question ID")
    interviewer: InterviewerPersona
    question_text: str = Field(description="Verbatim question asked")
    context_hint: str = Field(default="", description="Hint on what the interviewer is probing for")
    category: Literal["system_design", "deep_technical", "behavioral_star", "culture_fit", "stress_handling"] = Field(
        default="deep_technical",
        description="Question category",
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")


class TurnEvaluation(BaseModel):
    """Realtime evaluation of a single candidate answer by the Silent Judge."""

    score: int = Field(ge=0, le=100, description="Overall score for this turn")
    technical_depth_score: int = Field(ge=0, le=30, default=25, description="Technical accuracy & depth (0-30)")
    star_structure_score: int = Field(ge=0, le=25, default=20, description="STAR structure completeness (0-25)")
    confidence_score: int = Field(ge=0, le=25, default=22, description="Confidence, clarity and tone (0-25)")
    adaptability_score: int = Field(ge=0, le=20, default=18, description="Handling pressure & adaptability (0-20)")
    feedback: str = Field(description="Direct critique from the Judge on what was good and what was lacking")
    key_strengths: list[str] = Field(default_factory=list, description="Points candidate handled well")
    improvement_areas: list[str] = Field(default_factory=list, description="Points that could be sharper")
    ideal_star_answer: str = Field(description="Exemplary Harvard-style STAR benchmark answer for this question")


class InterviewTurn(BaseModel):
    """Single turn representing an interviewer question and candidate response."""

    turn_index: int = Field(description="Turn sequence number (1, 2, 3...)")
    question: QuestionItem
    candidate_answer: str | None = Field(default=None, description="Candidate response text")
    evaluation: TurnEvaluation | None = Field(default=None, description="Evaluation by Silent Judge")


class CandidateAssessmentReport(BaseModel):
    """Comprehensive post-interview evaluation report."""

    session_id: str
    candidate_name: str
    target_role: str
    total_turns_completed: int
    overall_score: int = Field(ge=0, le=100, description="Weighted average score across all turns")
    overall_grade: Literal["A+", "A", "B+", "B", "C"] = Field(default="A")
    verdict: str = Field(description="Final hiring decision verdict")
    technical_average: float
    star_structure_average: float
    confidence_average: float
    adaptability_average: float
    top_strengths: list[str] = Field(default_factory=list)
    critical_growth_areas: list[str] = Field(default_factory=list)
    actionable_prep_tips: list[str] = Field(default_factory=list)


class InterviewSession(BaseModel):
    """Full state of a live or completed multi-agent mock interview."""

    session_id: str
    candidate_id: str
    candidate_name: str
    target_role: str
    turns: list[InterviewTurn] = Field(default_factory=list)
    current_turn_index: int = Field(default=0)
    is_completed: bool = Field(default=False)
    final_report: CandidateAssessmentReport | None = Field(default=None)
