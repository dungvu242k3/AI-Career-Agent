"""API Request and Response DTO Schemas for CV Endpoints."""

from pydantic import BaseModel, Field
from ai.models.candidate import CandidateProfile


class UploadResponse(BaseModel):
    """Response payload returned upon CV file upload and parsing."""

    candidate_id: int = Field(description="Database unique ID for candidate")
    filename: str = Field(description="Original uploaded filename")
    text_length: int = Field(description="Character length of extracted text")
    profile: CandidateProfile = Field(description="Structured canonical candidate profile")
    is_cached: bool = Field(default=False, description="True if retrieved from checksum cache")


class UpdateProfileRequest(BaseModel):
    """Payload for updating candidate profile after user review/edit."""

    profile: CandidateProfile = Field(description="Updated CandidateProfile object")


class MessageResponse(BaseModel):
    """Generic status/message response."""

    message: str
    candidate_id: int
