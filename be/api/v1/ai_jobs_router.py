"""Owner-scoped asynchronous entry points for expensive AI work."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
import re
import uuid

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

from be.api.v1.schemas import AIJobAccepted, AIJobStatus, GenerateCVRequest
from be.config import Settings, get_settings
from be.core.security import CurrentUser, require_current_user
from be.core.storage import BaseStorageService, get_storage_service
from be.core.rate_limiter import cv_generation_rate_limiter, upload_rate_limiter
from be.db.database import create_ai_job, get_ai_job, get_candidate


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-jobs", tags=["AI Jobs"])
_ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    extension = Path(name).suffix.lower()
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and DOCX files are supported")
    stem = re.sub(r"[^a-zA-Z0-9_.-]", "_", Path(name).stem).strip("._")
    return f"{stem or f'cv_{uuid.uuid4().hex[:8]}'}{extension}"


async def _dispatch(job_id: str) -> None:
    """Queue by id only; the worker reloads protected input from storage/DB."""
    try:
        from be.workers.ai_task_worker import process_ai_job

        process_ai_job.delay(job_id)
    except Exception:
        # Do not lose the durable job if the broker is temporarily unavailable.
        # A healthy worker/reconciler can pick up queued jobs later.
        logger.exception("AI job %s was persisted but could not be dispatched", job_id)


def _accepted(job: dict) -> AIJobAccepted:
    return AIJobAccepted(
        job_id=job["id"],
        status=job["status"],
        poll_url=f"/api/v1/ai-jobs/{job['id']}",
    )


@router.post("/cv-ingestion", response_model=AIJobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_cv_ingestion(
    file: UploadFile = File(...),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    settings: Settings = Depends(get_settings),
    storage: BaseStorageService = Depends(get_storage_service),
    current_user: CurrentUser = Depends(require_current_user),
    _: None = Depends(upload_rate_limiter),
) -> AIJobAccepted:
    """Store a CV then enqueue extraction; no document bytes enter the broker."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A filename is required")
    safe_name = _safe_filename(file.filename)
    limit = settings.max_upload_size_mb * 1024 * 1024
    buffer = bytearray()
    while chunk := await file.read(64 * 1024):
        buffer.extend(chunk)
        if len(buffer) > limit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds the upload limit")
    content = bytes(buffer)
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    checksum = hashlib.sha256(content).hexdigest()
    storage_key, _ = await storage.upload_file(
        content,
        safe_name,
        "application/pdf" if safe_name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        str(current_user.id),
    )
    job, duplicate = await create_ai_job(
        owner_user_id=current_user.id,
        operation="cv-ingestion",
        idempotency_key=idempotency_key or checksum,
        payload={"storage_key": storage_key, "filename": safe_name, "checksum": checksum},
        model_version=f"routing:{settings.ai_provider}",
        prompt_version="grounded-v1",
    )
    if duplicate:
        await storage.delete_file(storage_key)
    else:
        await _dispatch(job["id"])
    return _accepted(job)


@router.post("/cv-generation", response_model=AIJobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_cv_generation(
    payload: GenerateCVRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    settings: Settings = Depends(get_settings),
    current_user: CurrentUser = Depends(require_current_user),
    _: None = Depends(cv_generation_rate_limiter),
) -> AIJobAccepted:
    """Queue CV composition/rendering with a durable, owner-bound request."""
    candidate = await get_candidate(payload.candidate_id, current_user.id)
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate was not found")
    request_key = idempotency_key or hashlib.sha256(payload.model_dump_json().encode()).hexdigest()
    job, duplicate = await create_ai_job(
        owner_user_id=current_user.id,
        operation="cv-generation",
        idempotency_key=request_key,
        payload=payload.model_dump(mode="json"),
        model_version=f"routing:{settings.ai_provider}",
        prompt_version="grounded-v1",
    )
    if not duplicate:
        await _dispatch(job["id"])
    return _accepted(job)


@router.get("/{job_id}", response_model=AIJobStatus)
async def get_job_status(job_id: str, current_user: CurrentUser = Depends(require_current_user)) -> AIJobStatus:
    job = await get_ai_job(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI job was not found")
    return AIJobStatus(
        job_id=job["id"],
        operation=job["operation"],
        status=job["status"],
        progress=job["progress"],
        result=job.get("result_json"),
        error_code=job.get("error_code"),
        trace_id=job.get("trace_id"),
        attempts=job["attempts"],
    )
