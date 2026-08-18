"""API Request and Response DTO Schemas for CV Endpoints."""

from typing import Literal
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
    """Payload for generating tailored Harvard 1-Page CV."""

    candidate_id: str = Field(description="Candidate profile UUIDv7 ID")
    jd_text: str = Field(description="Raw Job Description text", min_length=15, max_length=10000)
    language: Literal["vi", "en"] = Field(default="vi", description="Target CV language: 'vi' or 'en'")
    format: Literal["pdf"] = Field(default="pdf", description="Export format: 'pdf'")


