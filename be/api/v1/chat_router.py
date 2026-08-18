"""Chat & Job Search Router for Interactive Career Copilot (Cột 2 Workspace)."""

import json
import logging
from typing import Any
from fastapi import APIRouter, HTTPException, Query, status

from be.api.v1.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    JobItemSchema,
    JobSearchResponse,
)
from be.core.job_search import (
    detect_candidate_domain,
    get_job_by_id,
    search_jobs,
)
from be.db.database import get_candidate
from ai.guardrails.prompt_shield import PromptShieldEngine
from be.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Chat & Job Search"])
_prompt_shield = PromptShieldEngine()


@router.post(
    "/chat/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with Career Copilot or trigger Multi-Channel Job Search",
)
async def handle_chat_message(request: ChatMessageRequest) -> ChatMessageResponse:
    """Process user message in Workspace Copilot, auto-detecting job search intent and domain."""
    # 0. Safety Guardrails & Anti-Jailbreak Protection
    shield_result = _prompt_shield.scan_and_sanitize(request.message)
    if not shield_result.is_safe:
        return ChatMessageResponse(
            reply=(
                f"⚠️ **Cảnh báo bảo vệ AI Guardrails:** Tin nhắn của bạn bị chặn do chứa mẫu tấn công tiềm ẩn "
                f"({', '.join(shield_result.detected_threats)}). Vui lòng đặt câu hỏi phù hợp nhé!"
            ),
            detected_intent="security_blocked",
            jobs_found=[],
        )

    user_msg = shield_result.sanitized_text.strip().lower()
    
    # 1. Fetch Candidate Context if available
    candidate_profile = None
    domain = request.domain_override
    exp_years = None
    candidate_name = "bạn"

    if request.candidate_id:
        try:
            cand_data = await get_candidate(request.candidate_id)
            if cand_data and "profile_json" in cand_data:
                profile_obj = cand_data["profile_json"]
                if isinstance(profile_obj, str):
                    profile_obj = json.loads(profile_obj)
                candidate_profile = profile_obj
                
                # Extract candidate attributes
                p_info = profile_obj.get("personal_info", {})
                candidate_name = p_info.get("full_name") or "bạn"
                cand_title = p_info.get("title", "")
                
                # Extract skills list for domain detection
                skills_tax = profile_obj.get("skills_taxonomy", {})
                all_skills: list[str] = []
                for group in skills_tax.values():
                    if isinstance(group, list):
                        all_skills.extend([s.get("name", "") if isinstance(s, dict) else str(s) for s in group])

                if not domain:
                    domain = detect_candidate_domain(cand_title, all_skills)

                meta = profile_obj.get("metadata", {})
                exp_years = meta.get("total_experience_years")
        except Exception as e:
            logger.warning("Could not load candidate profile for chat: %s", e)

    if not domain:
        domain = detect_candidate_domain(user_msg)

    # 2. Detect Intent: Job Search vs Advice/General Chat
    is_job_search = any(
        kw in user_msg
        for kw in [
            "tìm việc",
            "việc làm",
            "tuyển dụng",
            "công việc",
            "job",
            "jobs",
            "backend",
            "frontend",
            "fullstack",
            "devops",
            "mobile",
            "ai",
            "chuyên ngành",
            "vị trí",
            "kinh nghiệm",
        ]
    )

    if is_job_search:
        # Determine domain from message if explicitly stated
        if "backend" in user_msg:
            domain = "backend"
        elif "frontend" in user_msg or "front-end" in user_msg or "react" in user_msg:
            domain = "frontend"
        elif "fullstack" in user_msg or "full stack" in user_msg:
            domain = "fullstack"
        elif "devops" in user_msg or "cloud" in user_msg or "kubernetes" in user_msg:
            domain = "devops"
        elif "mobile" in user_msg or "flutter" in user_msg or "ios" in user_msg or "android" in user_msg:
            domain = "mobile"
        elif "ai" in user_msg or "data" in user_msg or "machine learning" in user_msg:
            domain = "ai_data"

        # Search jobs across channels with Hybrid Vector Search & Semantic Re-ranking
        cand_p = None
        if candidate_profile:
            try:
                cand_p = CandidateProfile.model_validate(candidate_profile)
            except Exception as e:
                logger.debug("Failed to validate candidate profile model for reranker: %s", e)

        matched_jobs = search_jobs(
            domain=domain,
            min_exp_years=exp_years,
            location=request.location,
            limit=8,
            candidate_profile=cand_p,
        )

        domain_display_map = {
            "backend": "Backend Development",
            "frontend": "Frontend Development",
            "fullstack": "Fullstack Engineering",
            "devops": "DevOps & Cloud Infrastructure",
            "mobile": "Mobile App Development",
            "ai_data": "AI & Data Engineering",
        }
        display_domain = domain_display_map.get(domain, domain.capitalize())
        exp_text = f" với khoảng **{exp_years} năm kinh nghiệm**" if exp_years else ""

        reply_text = (
            f"🎯 Tôi đã quét và tổng hợp **{len(matched_jobs)} việc làm {display_domain}**{exp_text} "
            f"từ các kênh tuyển dụng hàng đầu (**ITviec, TopCV, VietnamWorks, LinkedIn**).\n\n"
            f"👉 Bạn có thể bấm **'Xem chi tiết'** trên từng thẻ công việc để đọc yêu cầu JD, "
            f"hoặc nhấn **'🎯 Nạp JD này'** để hệ thống tự động so khớp ATS và may đo CV chuẩn Harvard nhé!"
        )

        return ChatMessageResponse(
            reply=reply_text,
            detected_intent="job_search",
            jobs_found=matched_jobs,
        )

    # 3. Regular Career / CV Advice Logic
    # LLM-based or smart response
    settings = get_settings()
    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            prompt_context = (
                f"Bạn là Chuyên gia Cố vấn Hướng nghiệp AI (CareerPilot Copilot). "
                f"Đang tư vấn cho ứng viên tên '{candidate_name}' (Chuyên ngành: {domain}, Kinh nghiệm: {exp_years or 'Chưa rõ'} năm). "
                f"Trả lời người dùng ngắn gọn, súc tích, thực tế, định dạng markdown đẹp."
            )
            completion = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": request.message},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            ai_reply = completion.choices[0].message.content or "Tôi đã nhận câu hỏi của bạn."
            return ChatMessageResponse(
                reply=ai_reply,
                detected_intent="cv_advice",
                jobs_found=[],
            )
        except Exception as e:
            logger.warning("OpenAI chat error, fallback to built-in guidance: %s", e)

    # Fallback smart guidance
    advice_reply = (
        f"💡 **Tư vấn hướng nghiệp cho {candidate_name} ({domain.upper()}):**\n\n"
        f"1. **Tối ưu hóa kinh nghiệm:** Khi viết CV, hãy sử dụng công thức định lượng **STAR** (Situation - Task - Action - Result) thay vì chỉ liệt kê đầu việc.\n"
        f"2. **So khớp từ khóa:** Kiểm tra kỹ các kỹ năng cốt lõi trong JD mục tiêu để đảm bảo CV vượt qua các bộ lọc ATS tự động.\n"
        f"3. **Tìm việc:** Bạn có thể nhập câu lệnh ví dụ: *'Tìm việc {domain} tại TP.HCM'* hoặc *'Tìm việc {domain} remote'* để tôi quét các cơ hội tuyển dụng mới nhất!"
    )

    return ChatMessageResponse(
        reply=advice_reply,
        detected_intent="cv_advice",
        jobs_found=[],
    )


@router.get(
    "/jobs/by-domain",
    response_model=JobSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve jobs filtered by domain, experience level, location, and platform",
)
async def get_jobs_by_domain_endpoint(
    domain: str = Query(default="backend", description="Domain: backend, frontend, fullstack, devops, mobile, ai_data"),
    exp_years: float | None = Query(default=None, description="Candidate years of experience"),
    candidate_id: str | None = Query(default=None, description="Candidate profile ID for semantic re-ranking"),
    location: str | None = Query(default=None, description="Location: Hà Nội, TP.HCM, Remote, etc."),
    platform: str | None = Query(default=None, description="Platform: ITviec, TopCV, VietnamWorks, LinkedIn"),
    keyword: str | None = Query(default=None, description="Keyword search in title or skills"),
) -> JobSearchResponse:
    """Retrieve filtered job postings matching candidate criteria with optional semantic re-ranking."""
    cand_p = None
    if candidate_id:
        try:
            cand_data = await get_candidate(candidate_id)
            if cand_data and "profile_json" in cand_data:
                profile_raw = cand_data["profile_json"]
                cand_p = CandidateProfile.model_validate_json(profile_raw) if isinstance(profile_raw, str) else CandidateProfile.model_validate(profile_raw)
        except Exception as e:
            logger.debug("Could not load candidate profile for domain jobs endpoint: %s", e)

    jobs = search_jobs(
        domain=domain,
        min_exp_years=exp_years,
        location=location,
        platform=platform,
        keyword=keyword,
        limit=20,
        candidate_profile=cand_p,
    )
    return JobSearchResponse(
        total=len(jobs),
        domain=domain,
        jobs=jobs,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=JobItemSchema,
    status_code=status.HTTP_200_OK,
    summary="Get full job details by ID",
)
async def get_job_details_endpoint(job_id: str) -> JobItemSchema:
    """Get single job details including description, requirements and benefits."""
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with ID '{job_id}' not found")
    return job
