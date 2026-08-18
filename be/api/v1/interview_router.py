"""API Router for Adversarial Multi-Agent Mock Interview Arena (tab /interview)."""

import json
import logging
from typing import Literal
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ai.analysis.interview_arena import InterviewArenaEngine
from ai.guardrails.prompt_shield import PromptShieldEngine
from ai.models.candidate import CandidateProfile
from ai.models.interview import CandidateAssessmentReport, InterviewSession
from be.db.database import get_candidate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interview", tags=["Mock Interview Arena"])

# In-memory session store with bounded capacity (max 500 active sessions)
MAX_CONCURRENT_SESSIONS = 500
ACTIVE_SESSIONS: dict[str, InterviewSession] = {}
arena_engine = InterviewArenaEngine()
prompt_shield = PromptShieldEngine()


def _store_session(session: InterviewSession) -> None:
    """Store session in memory, evicting oldest entry if exceeding capacity."""
    if len(ACTIVE_SESSIONS) >= MAX_CONCURRENT_SESSIONS:
        oldest_key = next(iter(ACTIVE_SESSIONS))
        ACTIVE_SESSIONS.pop(oldest_key, None)
    ACTIVE_SESSIONS[session.session_id] = session


class StartInterviewRequest(BaseModel):
    candidate_id: str = Field(description="Candidate profile ID")
    target_role: str = Field(default="Software Engineer", description="Target job title")
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
async def start_interview_session(payload: StartInterviewRequest) -> InterviewSession:
    """Initialize interview arena with Tech Lead Alex and HR Sarah questions."""
    cand_data = await get_candidate(payload.candidate_id)
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
        clean_jd = shield_jd.sanitized_text

    session = arena_engine.start_session(
        candidate_profile=cand_p,
        target_role=payload.target_role,
        jd_text=clean_jd,
    )
    _store_session(session)
    return session


@router.post(
    "/submit-answer",
    response_model=InterviewSession,
    status_code=status.HTTP_200_OK,
    summary="Submit response to current question and receive Silent Judge score",
)
async def submit_turn_answer(payload: SubmitAnswerRequest) -> InterviewSession:
    """Process candidate answer, evaluate via Silent Judge, and advance turn."""
    session = ACTIVE_SESSIONS.get(payload.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên phỏng vấn này hoặc phiên đã hết hạn.",
        )

    # 1. AI Safety & Prompt Shield Check
    shield_res = prompt_shield.scan_and_sanitize(payload.answer_text)
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

    target_turn = session.turns[turn_idx]
    target_turn.candidate_answer = shield_res.sanitized_text

    # Evaluate turn via Silent Judge
    evaluation = arena_engine.evaluate_turn_answer(target_turn, shield_res.sanitized_text)
    target_turn.evaluation = evaluation

    # Advance current turn index
    session.current_turn_index = turn_idx + 1
    if session.current_turn_index >= len(session.turns):
        session.is_completed = True
        session.final_report = arena_engine.generate_final_assessment(session)

    _store_session(session)
    return session


@router.get(
    "/session/{session_id}",
    response_model=InterviewSession,
    status_code=status.HTTP_200_OK,
    summary="Retrieve session state",
)
async def get_interview_session(session_id: str) -> InterviewSession:
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên phỏng vấn.",
        )
    return session
