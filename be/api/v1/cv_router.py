"""CV Router — API endpoints for CV upload, preview, and update."""

from functools import lru_cache
import hashlib
import logging
from pathlib import Path
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ai.models.candidate import CandidateProfile
from ai.parsers import PDFInvalidFormatError, PDFParsingError, PDFScanDetectedError
from ai.pipeline import CVIngestionPipeline, get_default_ingestion_pipeline
from be.api.v1.schemas import MessageResponse, UpdateProfileRequest, UploadResponse
from be.config import Settings, get_settings
from be.db.database import (
    get_candidate,
    get_upload_by_checksum,
    save_candidate,
    save_upload,
    update_candidate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@lru_cache(maxsize=1)
def get_cached_ingestion_pipeline() -> CVIngestionPipeline:
    """Cached pipeline singleton to avoid reloading prompt templates per request."""
    return get_default_ingestion_pipeline()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Parse CV Document",
    description="Accepts a PDF document, performs layout deconstruction, and extracts structured CandidateProfile via Gemini AI.",
)
async def upload_cv(
    file: UploadFile = File(..., description="PDF CV file (max 10MB, up to 5 pages)"),
    settings: Settings = Depends(get_settings),
    pipeline: CVIngestionPipeline = Depends(get_cached_ingestion_pipeline),
):
    """Upload a CV PDF file, deconstruct layout, extract structured profile via AI pipeline."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận tệp định dạng PDF (.pdf).",
        )

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kích thước tệp quá lớn ({len(content) / (1024*1024):.1f}MB). Giới hạn tối đa là {settings.max_upload_size_mb}MB.",
        )

    # Compute SHA256 checksum for deduplication & instant cache retrieval
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

    # Save physical file to disk safely
    file_id = uuid.uuid4().hex[:8]
    upload_dir = settings.upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{file_id}_{file.filename}"
    file_path.write_bytes(content)

    # Execute AI Ingestion Pipeline (PyMuPDF -> Gemini Flash -> CandidateProfile v3)
    try:
        raw_text, profile = await pipeline.process_bytes(content, filename=file.filename)
    except PDFScanDetectedError as e:
        file_path.unlink(missing_ok=True)  # Clean up failed upload file
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (PDFInvalidFormatError, PDFParsingError) as e:
        file_path.unlink(missing_ok=True)  # Clean up failed upload file
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        file_path.unlink(missing_ok=True)  # Clean up failed upload file
        logger.error("Unhandled error during AI extraction: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi AI trích xuất hồ sơ: {e}",
        )

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


@router.get(
    "/preview/{candidate_id}",
    response_model=CandidateProfile,
    summary="Get Candidate Profile for Preview",
)
async def get_candidate_preview(candidate_id: int):
    """Retrieve CandidateProfile for preview and editing."""
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ ứng viên #{candidate_id}",
        )

    return CandidateProfile.model_validate_json(candidate["profile_json"])


@router.put(
    "/preview/{candidate_id}",
    response_model=MessageResponse,
    summary="Update Candidate Profile after User Edits",
)
async def update_candidate_preview(candidate_id: int, payload: UpdateProfileRequest):
    """Update CandidateProfile after user edits information on Preview Card."""
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ ứng viên #{candidate_id}",
        )

    profile = payload.profile
    success = await update_candidate(
        candidate_id=candidate_id,
        profile_json=profile.model_dump_json(),
        full_name=profile.full_name,
        email=profile.email,
        title=profile.title,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật hồ sơ.",
        )

    return MessageResponse(
        message="Cập nhật thông tin hồ sơ thành công.",
        candidate_id=candidate_id,
    )
