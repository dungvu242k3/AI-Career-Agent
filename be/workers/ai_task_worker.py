"""Idempotent Celery worker for durable AI jobs.

The broker carries only the job id.  CV bytes, prompts and PII remain in the
application's protected storage/database.
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
import logging
from typing import Any, TypeVar

from celery.signals import worker_process_shutdown

from ai.analysis.ats_matcher import get_default_ats_matcher
from ai.analysis.reflective_synthesizer import ReflectiveHarvardSynthesizer
from ai.execution import (
    AIErrorCode,
    AIExecutionError,
    AIExecutor,
    bind_ai_owner,
    get_last_ai_trace_id,
    reset_ai_owner,
)
from ai.models.candidate import CandidateProfile
from ai.parsers.jd_parser import get_default_jd_parser
from be.api.v1.schemas import GenerateCVRequest
from be.core.cv_renderer import get_cv_renderer
from be.core.redis_client import close_redis_client
from be.core.storage import get_storage_service
from be.db.database import (
    claim_ai_job,
    close_db,
    complete_ai_job,
    fail_ai_job,
    get_candidate,
    init_db,
    list_queued_ai_job_ids,
    requeue_ai_job,
    save_candidate_and_upload_idempotently,
)
from be.workers.celery_app import celery_app
from ai.pipeline import get_default_ingestion_pipeline
from be.telemetry import shutdown_telemetry


logger = logging.getLogger(__name__)
_db_initialized = False
_worker_loop: asyncio.AbstractEventLoop | None = None
T = TypeVar("T")


def run_in_worker_loop(coroutine: Coroutine[Any, Any, T]) -> T:
    """Run tasks on one event loop per Celery child process.

    ``asyncpg`` connections are tied to their event loop. Celery can retry the
    same task in one prefork child, so ``asyncio.run`` per invocation would
    reuse a database pool from a closed/different loop. Keeping this loop for
    the child lifetime makes retries and scheduled reconciliation safe.
    """
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


@worker_process_shutdown.connect
def close_worker_process_resources(**_: Any) -> None:
    """Release async clients on the event loop that created them."""
    global _worker_loop, _db_initialized
    if _worker_loop is None or _worker_loop.is_closed():
        return

    async def close_resources() -> None:
        await close_db()
        await close_redis_client()

    try:
        _worker_loop.run_until_complete(close_resources())
    finally:
        shutdown_telemetry()
        _worker_loop.close()
        _worker_loop = None
        _db_initialized = False


async def _ensure_db() -> None:
    global _db_initialized
    if not _db_initialized:
        await init_db()
        _db_initialized = True


async def _run_ingestion(job: dict) -> dict:
    payload = job["payload_json"]
    owner_user_id = job["owner_user_id"]
    storage = get_storage_service()
    content = await storage.get_file_bytes(payload["storage_key"])
    raw_text, profile = await get_default_ingestion_pipeline().process_bytes(content, payload["filename"])
    candidate_id, duplicate = await save_candidate_and_upload_idempotently(
        profile_json=profile.model_dump_json(),
        full_name=profile.full_name,
        email=profile.email,
        title=profile.title,
        owner_user_id=owner_user_id,
        filename=payload["filename"],
        file_path=payload["storage_key"],
        checksum=payload["checksum"],
        raw_text=raw_text,
    )
    return {
        "candidate_id": candidate_id,
        "filename": payload["filename"],
        "text_length": len(raw_text),
        "storage_key": payload["storage_key"],
        "is_cached": duplicate,
        "profile": profile.model_dump(mode="json"),
    }


async def _run_generation(job: dict) -> dict:
    payload = GenerateCVRequest.model_validate(job["payload_json"])
    candidate = await get_candidate(payload.candidate_id, job["owner_user_id"])
    if not candidate:
        raise AIExecutionError(AIErrorCode.INVALID_RESPONSE, "Candidate was deleted before generation")
    profile_raw = candidate["profile_json"]
    profile = CandidateProfile.model_validate_json(profile_raw) if isinstance(profile_raw, str) else CandidateProfile.model_validate(profile_raw)
    jd = await get_default_jd_parser().parse_jd_text(payload.jd_text)
    ats_report = await get_default_ats_matcher().match(profile, jd)
    cv_data, reflection = await ReflectiveHarvardSynthesizer().synthesize(profile, jd, ats_report, payload.language)
    pdf_bytes = get_cv_renderer(payload.template).render(cv_data)
    storage_key, _ = await get_storage_service().upload_file(
        pdf_bytes,
        f"generated_cv_{job['id']}.pdf",
        "application/pdf",
        str(job["owner_user_id"]),
    )
    return {
        "storage_key": storage_key,
        "ats_score": cv_data.ats_score_estimate,
        "word_count": cv_data.estimated_word_count,
        "critic_score": reflection.final_critic_score,
        "critic_approved": reflection.is_converged,
        "reflection_iterations": reflection.iterations_count,
        "grounding": reflection.grounding_report,
    }


async def _cleanup_terminal_failure(job: dict) -> None:
    """Remove unreferenced ingress bytes after a terminal ingestion failure."""
    if job.get("operation") != "cv-ingestion":
        return
    storage_key = (job.get("payload_json") or {}).get("storage_key")
    if not storage_key:
        return
    try:
        await get_storage_service().delete_file(storage_key)
    except Exception:
        # This must not hide the normalized job failure; a scheduled storage
        # lifecycle policy is the final backstop.
        logger.warning("Failed to clean up terminal AI ingestion storage object")


async def _execute_job(job_id: str, max_retries: int) -> dict:
    await _ensure_db()
    job = await claim_ai_job(job_id)
    if not job:
        return {"status": "already_claimed", "retry": False}
    owner_context = bind_ai_owner(job["owner_user_id"])
    try:
        if job["operation"] == "cv-ingestion":
            result = await _run_ingestion(job)
        elif job["operation"] == "cv-generation":
            result = await _run_generation(job)
        else:
            raise AIExecutionError(AIErrorCode.INVALID_RESPONSE, "Unsupported AI job operation")
        await complete_ai_job(job_id, result, trace_id=get_last_ai_trace_id())
        return {"status": "succeeded", "retry": False, "result": result}
    except AIExecutionError as error:
        if error.retryable and job["attempts"] < max_retries:
            await requeue_ai_job(job_id, error.code.value)
            return {"status": "queued", "retry": True, "error_code": error.code.value}
        await fail_ai_job(job_id, error.code.value, trace_id=get_last_ai_trace_id())
        await _cleanup_terminal_failure(job)
        return {"status": "failed", "retry": False, "error_code": error.code.value}
    except Exception as error:
        logger.exception("AI job %s failed without exposing provider details", job_id)
        if AIExecutor.is_retryable(error) and job["attempts"] < max_retries:
            await requeue_ai_job(job_id, AIErrorCode.PROVIDER_UNAVAILABLE.value)
            return {
                "status": "queued",
                "retry": True,
                "error_code": AIErrorCode.PROVIDER_UNAVAILABLE.value,
            }
        await fail_ai_job(job_id, AIErrorCode.INVALID_RESPONSE.value, trace_id=get_last_ai_trace_id())
        await _cleanup_terminal_failure(job)
        return {"status": "failed", "retry": False, "error_code": AIErrorCode.INVALID_RESPONSE.value}
    finally:
        reset_ai_owner(owner_context)


@celery_app.task(bind=True, max_retries=3, name="be.workers.process_ai_job")
def process_ai_job(self, job_id: str):
    """Execute one durable job; duplicate Celery deliveries are harmless."""
    outcome = run_in_worker_loop(_execute_job(job_id, self.max_retries))
    if outcome.get("retry"):
        retry_number = max(self.request.retries, 0)
        raise self.retry(
            exc=RuntimeError(outcome["error_code"]),
            countdown=min(60, 2 ** retry_number),
        )
    return outcome


@celery_app.task(name="be.workers.reconcile_queued_ai_jobs")
def reconcile_queued_ai_jobs():
    """Re-dispatch durable queued jobs after a transient broker/API outage."""
    async def enqueue() -> int:
        await _ensure_db()
        job_ids = await list_queued_ai_job_ids(limit=100)
        for queued_id in job_ids:
            process_ai_job.delay(queued_id)
        return len(job_ids)

    return run_in_worker_loop(enqueue())
