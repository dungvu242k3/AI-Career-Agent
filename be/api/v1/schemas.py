"""API Request and Response DTO Schemas for CV Endpoints."""

from pydantic import BaseModel, Field
from ai.models.candidate import CandidateProfile


class UploadResponse(BaseModel):
    """Response payload returned upon CV file upload and parsing."""

    candidate_id: int = Field(description="Database unique ID for candidate")
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
    candidate_id: int


class STARRewriteRequest(BaseModel):
    """Payload for requesting STAR bullet point rewrite."""

    raw_input: str = Field(description="Weak bullet point or missing skill name", min_length=2)
    target_role: str = Field(default="Software Engineer", description="Target job title")
    context: str | None = Field(default=None, description="Optional background context")


class JDMatchRequest(BaseModel):
    """JSON payload for JD matching via raw text."""

    candidate_id: int = Field(description="Candidate profile ID")
    jd_text: str = Field(description="Raw Job Description text", min_length=15, max_length=10000)


class ATSHistoryItem(BaseModel):
    """Single historical ATS analysis record."""

    id: int
    candidate_id: int
    ats_score: int
    ats_grade: str
    report_json: str
    created_at: str | None = None

