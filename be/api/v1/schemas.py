"""API Request and Response DTO Schemas for CV Endpoints."""

from typing import Any, Literal
from pydantic import BaseModel, Field
from ai.models.candidate import CandidateProfile


class UploadResponse(BaseModel):
    """Response payload returned upon CV file upload and parsing."""

    candidate_id: str = Field(description="Database UUIDv7 for candidate")
    filename: str = Field(description="Original uploaded filename")
    text_length: int = Field(description="Character length of extracted text")
    profile: CandidateProfile = Field(description="Structured canonical candidate profile")
    storage_key: str | None = Field(default=None, description="Storage object key in MinIO / S3 / Local")
    presigned_url: str | None = Field(default=None, description="Temporary presigned URL for secure viewing")
    is_cached: bool = Field(default=False, description="True if retrieved from checksum cache")


class UpdateProfileRequest(BaseModel):
    """Payload for updating candidate profile after user review/edit."""

    profile: CandidateProfile = Field(description="Updated CandidateProfile object")


class MessageResponse(BaseModel):
    """Generic status/message response."""

    message: str
    candidate_id: str | None = None


class AIJobAccepted(BaseModel):
    """Asynchronous AI work accepted for processing."""

    job_id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    poll_url: str


class AIJobStatus(BaseModel):
    """Owner-scoped job state; result has no raw prompt or provider exception."""

    job_id: str
    operation: Literal["cv-ingestion", "cv-generation"]
    status: Literal["queued", "running", "succeeded", "failed"]
    progress: int = Field(ge=0, le=100)
    result: dict[str, Any] | None = None
    error_code: str | None = None
    trace_id: str | None = None
    attempts: int = Field(ge=0)


class STARRewriteRequest(BaseModel):
    """Payload for requesting STAR bullet point rewrite."""

    raw_input: str = Field(description="Weak bullet point or missing skill name", min_length=2)
    target_role: str = Field(default="Software Engineer", description="Target job title")
    context: str | None = Field(default=None, description="Optional background context")


class JDMatchRequest(BaseModel):
    """JSON payload for JD matching via raw text."""

    candidate_id: str = Field(description="Candidate profile UUIDv7 ID")
    jd_text: str = Field(description="Raw Job Description text", min_length=15, max_length=10000)


class ATSHistoryItem(BaseModel):
    """Single historical ATS analysis record."""

    id: int
    candidate_id: str
    ats_score: int
    ats_grade: str
    report_json: str
    created_at: str | None = None


class GenerateCVRequest(BaseModel):
    """Payload for generating tailored Harvard / Modern Tech / Executive 1-Page CV."""

    candidate_id: str = Field(description="Candidate profile UUIDv7 ID")
    jd_text: str = Field(description="Raw Job Description text", min_length=15, max_length=10000)
    language: Literal["vi", "en"] = Field(default="vi", description="Target CV language: 'vi' or 'en'")
    template: Literal["harvard", "modern_tech", "executive"] = Field(default="harvard", description="Template style: 'harvard', 'modern_tech', 'executive'")
    format: Literal["pdf"] = Field(default="pdf", description="Export format: 'pdf'")


class JobItemSchema(BaseModel):
    """Schema representing a job post across recruitment channels."""

    id: str = Field(description="Unique identifier for the job")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    platform: str = Field(description="Recruitment channel: ITviec, TopCV, VietnamWorks, LinkedIn")
    platform_color: str = Field(default="#10b981", description="Theme color for platform badge")
    experience_required: str = Field(description="Human readable experience requirement (e.g. '2 - 4 năm kinh nghiệm')")
    min_years_exp: float = Field(default=0.0, description="Minimum years of experience required")
    max_years_exp: float = Field(default=10.0, description="Maximum years of experience required")
    domain: str = Field(description="Domain/Specialization: backend, frontend, fullstack, mobile, devops, ai_data, qa, other")
    location: str = Field(description="Job location (Hà Nội, TP.HCM, Remote, Hybrid...)")
    salary_range: str = Field(default="Thoả thuận", description="Salary range")
    job_url: str = Field(description="Original URL link to the job post")
    skills: list[str] = Field(default_factory=list, description="Primary tech stack skills required")
    description: str = Field(default="", description="Detailed job summary and responsibilities")
    requirements: str = Field(default="", description="Detailed job requirements")
    benefits: str = Field(default="", description="Company benefits and perks")
    posted_date: str = Field(default="Vừa đăng", description="Posting timestamp or date")
    semantic_fit_score: int | None = Field(default=None, description="Deprecated compatibility alias for heuristic_fit_score")
    heuristic_fit_score: int | None = Field(default=None, description="Lexical fit heuristic (0-100); discovery hint only, not a hiring decision")
    fit_highlights: list[str] = Field(default_factory=list, description="Key matching strengths identified by AI")


class JobSearchResponse(BaseModel):
    """Response payload for job search by domain/experience."""

    total: int
    domain: str
    jobs: list[JobItemSchema]


class ChatMessageRequest(BaseModel):
    """Payload for user interaction with AI Career & Job Search Copilot."""

    message: str = Field(description="User chat message", min_length=1)
    candidate_id: str | None = Field(default=None, description="Optional candidate profile ID for context")
    domain_override: str | None = Field(default=None, description="Optional domain filter override")
    location: str | None = Field(default=None, description="Optional location filter")


class ChatMessageResponse(BaseModel):
    """Response returned from AI Career & Job Search Copilot."""

    reply: str = Field(description="AI response text in markdown")
    detected_intent: str = Field(default="general_chat", description="Intent: 'job_search', 'cv_advice', 'general_chat'")
    jobs_found: list[JobItemSchema] = Field(default_factory=list, description="List of matched jobs if job search was requested")
    error_code: str | None = Field(default=None, description="Stable AI safety/provider error code when no AI answer is produced")
