"""API Router for Adversarial Multi-Agent Mock Interview Arena (tab /interview)."""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ai.analysis.interview_arena import InterviewArenaEngine
from ai.guardrails.prompt_shield import PromptShieldEngine
from ai.models.candidate import CandidateProfile
from ai.models.interview import InterviewSession
from be.db.database import get_candidate
from be.core.rate_limiter import interview_rate_limiter
from be.core.redis_client import get_redis_client
from be.core.security import CurrentUser, require_current_user
from be.config import get_settings
from be.api.v1.ai_context import ai_request_context

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interview", tags=["Mock Interview Arena"], dependencies=[Depends(ai_request_context)])

# In-memory session store with bounded capacity (fallback if Redis is unavailable)
MAX_CONCURRENT_SESSIONS = 500
ACTIVE_SESSIONS: dict[str, "StoredSession"] = {}
_memory_session_lock = asyncio.Lock()
arena_engine = InterviewArenaEngine()
prompt_shield = PromptShieldEngine()


class StoredSession(BaseModel):
    """Private session envelope; never returned directly to an API client."""

    owner_user_id: int
    version: int = 0
    session: InterviewSession


async def _store_session(record: StoredSession, expected_version: int | None = None) -> bool:
    """Persist with compare-and-set so concurrent answers cannot overwrite state."""
    key = f"interview_session:{record.session.session_id}"
    try:
        redis_client = await get_redis_client()
        if redis_client:
            async with redis_client.pipeline() as pipe:
                await pipe.watch(key)
                current = await pipe.get(key)
                if expected_version is not None:
                    if not current or StoredSession.model_validate_json(current).version != expected_version:
                        await pipe.reset()
                        return False
                elif current:
                    await pipe.reset()
                    return False
                pipe.multi()
                pipe.set(key, record.model_dump_json(), ex=3600)
                await pipe.execute()
                return True
    except Exception as e:
        logger.warning("Redis session persistence failed: %s", e)

    if get_settings().is_production:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview session service is temporarily unavailable.",
        )

    async with _memory_session_lock:
        current = ACTIVE_SESSIONS.get(record.session.session_id)
        if expected_version is not None and (not current or current.version != expected_version):
            return False
        if expected_version is None and current:
            return False
        if len(ACTIVE_SESSIONS) >= MAX_CONCURRENT_SESSIONS and not current:
            ACTIVE_SESSIONS.pop(next(iter(ACTIVE_SESSIONS)))
        ACTIVE_SESSIONS[record.session.session_id] = record
        return True


async def _get_session(session_id: str) -> StoredSession | None:
    """Get session from Redis or in memory."""
    try:
        redis_client = await get_redis_client()
        if redis_client:
            data = await redis_client.get(f"interview_session:{session_id}")
            if data:
                return StoredSession.model_validate_json(data)
    except Exception as e:
        logger.warning("Failed to get session from Redis, using fallback: %s", e)

    if get_settings().is_production:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Interview session service is temporarily unavailable.",
        )
        
    record = ACTIVE_SESSIONS.get(session_id)
    # Never hand the shared in-memory object to a caller: mutating it before
    # compare-and-set would defeat the version check.
    return record.model_copy(deep=True) if record else None


class StartInterviewRequest(BaseModel):
    candidate_id: str = Field(description="Candidate profile ID")
    target_role: str = Field(default="Software Engineer", description="Target job title")
    domain: str = Field(default="backend", description="Domain for routing")
    jd_text: str | None = Field(default=None, description="Optional JD text for targeted questions")


class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(description="Active interview session ID")
    turn_index: int = Field(description="Turn number being answered (1-indexed)")
    answer_text: str = Field(description="Candidate response text", min_length=5)


@router.post(
    "/start",
    response_model=InterviewSession,
    status_code=status.HTTP_200_OK,
    summary="Initialize a multi-agent mock interview session",
)
async def start_interview_session(
    payload: StartInterviewRequest,
    _ = Depends(interview_rate_limiter),
    current_user: CurrentUser = Depends(require_current_user),
) -> InterviewSession:
    """Initialize interview arena with Tech Lead Alex and HR Sarah questions."""
    cand_data = await get_candidate(payload.candidate_id, current_user.id)
    if not cand_data or "profile_json" not in cand_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ ứng viên #{payload.candidate_id}",
        )

    try:
        profile_raw = cand_data["profile_json"]
        cand_p = CandidateProfile.model_validate_json(profile_raw) if isinstance(profile_raw, str) else CandidateProfile.model_validate(profile_raw)
    except Exception as e:
        logger.error("Failed to parse candidate profile: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hồ sơ ứng viên trong cơ sở dữ liệu không hợp lệ.",
        )

    clean_jd = None
    if payload.jd_text:
        shield_jd = prompt_shield.scan_and_sanitize(payload.jd_text)
        if not shield_jd.is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "AI_INPUT_REJECTED", "message": "JD was rejected by the AI safety policy"},
            )
        clean_jd = shield_jd.sanitized_text

    session = await arena_engine.start_session(
        candidate_profile=cand_p,
        target_role=payload.target_role,
        domain=payload.domain,
        jd_text=clean_jd,
        tier=current_user.tier,
    )
    created = await _store_session(StoredSession(owner_user_id=current_user.id, session=session))
    if not created:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="KhÃ´ng thá»ƒ lÆ°u phiÃªn phá»ng váº¥n.")
    return session


@router.post(
    "/submit-answer",
    response_model=InterviewSession,
    status_code=status.HTTP_200_OK,
    summary="Submit response to current question and receive Silent Judge score",
)
async def submit_turn_answer(
    payload: SubmitAnswerRequest,
    _ = Depends(interview_rate_limiter),
    current_user: CurrentUser = Depends(require_current_user),
) -> InterviewSession:
    """Process candidate answer, evaluate via Silent Judge, and advance turn."""
    record = await _get_session(payload.session_id)
    if not record or record.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên phỏng vấn này hoặc phiên đã hết hạn.",
        )

    session = record.session
    # 1. AI Safety & Prompt Shield Check
    shield_res = prompt_shield.scan_and_sanitize(payload.answer_text)
    if not shield_res.is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI_INPUT_REJECTED: Câu trả lời vi phạm chính sách bảo mật AI.",
        )
    if not shield_res.is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Câu trả lời vi phạm chính sách bảo mật ({', '.join(shield_res.detected_threats)}). Vui lòng thử lại!",
        )

    turn_idx = payload.turn_index - 1
    if turn_idx < 0 or turn_idx >= len(session.turns):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lượt phỏng vấn #{payload.turn_index} không hợp lệ.",
        )

    if session.is_completed or turn_idx != session.current_turn_index:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="LÆ°á»£t phá»ng váº¥n Ä‘Ã£ thay Ä‘á»•i. Vui lÃ²ng táº£i láº¡i phiÃªn.")

    target_turn = session.turns[turn_idx]
    target_turn.candidate_answer = shield_res.sanitized_text

    # Evaluate turn via Silent Judge
    evaluation = await arena_engine.evaluate_turn_answer(session, target_turn, shield_res.sanitized_text)
    target_turn.evaluation = evaluation

    # Advance current turn index
    session.current_turn_index = turn_idx + 1
    if session.current_turn_index >= len(session.turns):
        session.is_completed = True
        session.final_report = arena_engine.generate_final_assessment(session)

    record.version += 1
    updated = await _store_session(record, expected_version=record.version - 1)
    if not updated:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PhiÃªn phá»ng váº¥n Ä‘Ã£ Ä‘Æ°á»£c cáº­p nháº­t á»Ÿ yÃªu cáº§u khÃ¡c.")
    return session


@router.get(
    "/session/{session_id}",
    response_model=InterviewSession,
    status_code=status.HTTP_200_OK,
    summary="Retrieve session state",
)
async def get_interview_session(session_id: str, current_user: CurrentUser = Depends(require_current_user)) -> InterviewSession:
    record = await _get_session(session_id)
    if not record or record.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên phỏng vấn.",
        )
    return record.session
