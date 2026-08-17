"""CV Router — API endpoints for CV upload, preview, update, and secure file streaming."""

from functools import lru_cache
import hashlib
import io
import logging
from pathlib import Path
import re
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import StreamingResponse

from ai.models.candidate import CandidateProfile
from ai.parsers import (
    PDFInvalidFormatError,
    PDFParsingError,
    PDFScanDetectedError,
    DocxInvalidFormatError,
    DocxParsingError,
)
from ai.pipeline import CVIngestionPipeline, get_default_ingestion_pipeline
from be.api.v1.schemas import MessageResponse, UpdateProfileRequest, UploadResponse
from be.config import Settings, get_settings
from be.core.rate_limiter import upload_rate_limiter, read_rate_limiter
from be.core.storage import BaseStorageService, get_storage_service
from be.db.database import (
    get_candidate,
    get_upload_by_checksum,
    save_candidate,
    save_upload,
    update_candidate,
)

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def sanitize_filename(filename: str) -> str:
    """Sanitize upload filename to prevent Path Traversal and illegal filesystem characters."""
    basename = Path(filename).name
    # Extract extension
    ext = Path(basename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".pdf"

    stem = Path(basename).stem
    safe_stem = re.sub(r"[^a-zA-Z0-9_.-]", "_", stem)
    if not safe_stem or safe_stem.startswith("."):
        safe_stem = f"cv_{uuid.uuid4().hex[:6]}"

    return f"{safe_stem}{ext}"


@lru_cache(maxsize=1)
def get_cached_ingestion_pipeline() -> CVIngestionPipeline:
    """Cached pipeline singleton to avoid reloading prompt templates per request."""
    return get_default_ingestion_pipeline()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Parse CV Document (PDF / DOCX)",
    description="Accepts a PDF or Word (.docx) document, uploads to MinIO/S3 object storage, and extracts structured CandidateProfile via AI pipeline.",
    dependencies=[Depends(upload_rate_limiter)],
)
async def upload_cv(
    file: UploadFile = File(..., description="PDF or Word CV file (max 2MB, up to 2 pages)"),
    settings: Settings = Depends(get_settings),
    pipeline: CVIngestionPipeline = Depends(get_cached_ingestion_pipeline),
    storage: BaseStorageService = Depends(get_storage_service),
):
    """Upload a CV file (PDF/DOCX), store in MinIO/S3, deconstruct layout, extract structured profile via AI pipeline."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên tệp không hợp lệ.",
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận tệp định dạng PDF (.pdf) hoặc Microsoft Word (.docx).",
        )

    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kích thước tệp quá lớn ({len(content) / (1024*1024):.1f}MB). Giới hạn tối đa là {settings.max_upload_size_mb}MB.",
        )

    # Sanitize filename against Path Traversal attacks
    safe_filename = sanitize_filename(file.filename)

    # Compute SHA256 checksum for deduplication & instant cache retrieval
    checksum = hashlib.sha256(content).hexdigest()
    cached_upload = await get_upload_by_checksum(checksum)
    if cached_upload and cached_upload["candidate_id"]:
        candidate = await get_candidate(cached_upload["candidate_id"])
        if candidate:
            profile = CandidateProfile.model_validate_json(candidate["profile_json"])
            presigned_url = await storage.get_presigned_url(cached_upload["file_path"])
            return UploadResponse(
                candidate_id=candidate["id"],
                filename=cached_upload["filename"],
                text_length=len(cached_upload["raw_text"] or ""),
                profile=profile,
                storage_key=cached_upload["file_path"],
                presigned_url=presigned_url,
                is_cached=True,
            )

    # Determine MIME content type
    content_type = file.content_type or (
        "application/pdf" if file_ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Upload to MinIO / S3 Object Storage (with local disk fallback)
    storage_key, presigned_url = await storage.upload_file(
        content=content,
        filename=safe_filename,
        content_type=content_type,
    )

    # Execute AI Ingestion Pipeline (PDF / DOCX -> AI Extractor -> CandidateProfile v3)
    try:
        raw_text, profile = await pipeline.process_bytes(content, filename=safe_filename)
    except PDFScanDetectedError as e:
        await storage.delete_file(storage_key)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (PDFInvalidFormatError, PDFParsingError, DocxInvalidFormatError, DocxParsingError) as e:
        await storage.delete_file(storage_key)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await storage.delete_file(storage_key)
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
        filename=safe_filename,
        file_path=storage_key,
        checksum=checksum,
        raw_text=raw_text,
        candidate_id=candidate_id,
    )

    return UploadResponse(
        candidate_id=candidate_id,
        filename=safe_filename,
        text_length=len(raw_text),
        profile=profile,
        storage_key=storage_key,
        presigned_url=presigned_url,
        is_cached=False,
    )


@router.get(
    "/preview/{candidate_id}",
    response_model=CandidateProfile,
    summary="Get Candidate Profile for Preview",
    dependencies=[Depends(read_rate_limiter)],
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
    dependencies=[Depends(read_rate_limiter)],
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


@router.get(
    "/file/{storage_key:path}",
    summary="Download or View Stored CV Document",
    dependencies=[Depends(read_rate_limiter)],
)
async def get_stored_file(
    storage_key: str,
    storage: BaseStorageService = Depends(get_storage_service),
):
    """Stream stored file bytes securely (for local storage or proxy mode)."""
    try:
        content = await storage.get_file_bytes(storage_key)
        ext = Path(storage_key).suffix.lower()
        media_type = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename={Path(storage_key).name}"},
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tệp.")
    except Exception as e:
        logger.error("Error retrieving file %s: %s", storage_key, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Lỗi khi tải tệp.")
