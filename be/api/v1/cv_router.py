"""CV Router — API endpoints for CV upload, preview, and update."""

import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from ai.pipeline import get_default_ingestion_pipeline
from ai.parsers import PDFParsingError, PDFScanDetectedError, PDFInvalidFormatError
from ai.models.candidate import CandidateProfile
from be.config import get_settings
from be.db.database import (
    save_candidate,
    update_candidate,
    save_upload,
    get_candidate,
    get_upload_by_checksum,
)

router = APIRouter()


class UploadResponse(BaseModel):
    candidate_id: int
    filename: str
    text_length: int
    profile: CandidateProfile
    is_cached: bool = False


class UpdateProfileRequest(BaseModel):
    profile: CandidateProfile


class MessageResponse(BaseModel):
    message: str
    candidate_id: int


@router.post("/upload", response_model=UploadResponse)
async def upload_cv(file: UploadFile = File(...)):
    """Upload a CV PDF file, deconstruct layout, extract structured profile via AI pipeline.

    Returns candidate ID and structured CandidateProfile v3 for the Preview Card.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận tệp định dạng PDF (.pdf).")

    settings = get_settings()
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Kích thước tệp quá lớn ({len(content) / (1024*1024):.1f}MB). Giới hạn tối đa là {settings.max_upload_size_mb}MB.",
        )

    # Compute SHA256 checksum for deduplication / caching
    checksum = hashlib.sha256(content).hexdigest()
    cached_upload = await get_upload_by_checksum(checksum)
    if cached_upload and cached_upload["candidate_id"]:
        candidate = await get_candidate(cached_upload["candidate_id"])
        if candidate:
            profile = CandidateProfile.model_validate_json(candidate["profile_json"])
            return UploadResponse(
                candidate_id=candidate["id"],
                filename=cached_upload["filename"],
                text_length=len(cached_upload["raw_text"] or ""),
                profile=profile,
                is_cached=True,
            )

    # Save physical file to disk
    file_id = uuid.uuid4().hex[:8]
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{file_id}_{file.filename}"
    file_path.write_bytes(content)

    # Execute AI Ingestion Pipeline (PyMuPDF -> Gemini Flash -> CandidateProfile v3)
    pipeline = get_default_ingestion_pipeline()
    try:
        raw_text, profile = await pipeline.process_bytes(content, filename=file.filename)
    except PDFScanDetectedError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (PDFInvalidFormatError, PDFParsingError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi AI trích xuất hồ sơ: {e}")

    # Persist in Database
    candidate_id = await save_candidate(
        profile_json=profile.model_dump_json(),
        full_name=profile.full_name,
        email=profile.email,
        title=profile.title,
    )
    await save_upload(
        filename=file.filename,
        file_path=str(file_path),
        checksum=checksum,
        raw_text=raw_text,
        candidate_id=candidate_id,
    )

    return UploadResponse(
        candidate_id=candidate_id,
        filename=file.filename,
        text_length=len(raw_text),
        profile=profile,
        is_cached=False,
    )


@router.get("/preview/{candidate_id}", response_model=CandidateProfile)
async def get_candidate_preview(candidate_id: int):
    """Retrieve CandidateProfile for preview and editing."""
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hồ sơ ứng viên #{candidate_id}")

    return CandidateProfile.model_validate_json(candidate["profile_json"])


@router.put("/preview/{candidate_id}", response_model=MessageResponse)
async def update_candidate_preview(candidate_id: int, payload: UpdateProfileRequest):
    """Update CandidateProfile after user edits information on Preview Card."""
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy hồ sơ ứng viên #{candidate_id}")

    profile = payload.profile
    success = await update_candidate(
        candidate_id=candidate_id,
        profile_json=profile.model_dump_json(),
        full_name=profile.full_name,
        email=profile.email,
        title=profile.title,
    )
    if not success:
        raise HTTPException(status_code=500, detail="Không thể cập nhật hồ sơ.")

    return MessageResponse(
        message="Cập nhật thông tin hồ sơ thành công.",
        candidate_id=candidate_id,
    )
