"""ATS Router — API endpoints for Job Description matching, ATS compatibility scoring, and STAR rewriting."""

from functools import lru_cache
import logging
from pathlib import Path
import re
import unicodedata

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from ai.analysis.ats_matcher import ATSMatcher, get_default_ats_matcher
from ai.analysis.star_rewriter import STARRewriter, get_default_star_rewriter
from ai.analysis.harvard_synthesizer import HarvardCVSynthesizer
from ai.models.candidate import CandidateProfile
from ai.models.jd import JDMatchReport, JDProfile
from ai.models.star import STARResult
from ai.parsers.jd_parser import (
    JDParser,
    get_default_jd_parser,
    ALLOWED_JD_EXTENSIONS,
    MAX_JD_FILE_SIZE_BYTES,
)
from be.api.v1.schemas import (
    ATSHistoryItem,
    STARRewriteRequest,
    GenerateCVRequest,
)
from be.core.cv_renderer import HarvardPDFRenderer, get_cv_renderer
from be.core.rate_limiter import (
    ats_rate_limiter,
    read_rate_limiter,
    star_rate_limiter,
    cv_generation_rate_limiter,
)
from be.db.database import (
    get_candidate,
    get_candidate_analyses,
    save_analysis,
)
from fastapi.responses import Response

logger = logging.getLogger(__name__)
router = APIRouter()


from ai.analysis.reflective_synthesizer import ReflectiveHarvardSynthesizer

@lru_cache(maxsize=1)
def get_cached_jd_parser() -> JDParser:
    return get_default_jd_parser()


@lru_cache(maxsize=1)
def get_cached_ats_matcher() -> ATSMatcher:
    return get_default_ats_matcher()


@lru_cache(maxsize=1)
def get_cached_star_rewriter() -> STARRewriter:
    return get_default_star_rewriter()


@lru_cache(maxsize=1)
def get_cached_harvard_synthesizer() -> ReflectiveHarvardSynthesizer:
    return ReflectiveHarvardSynthesizer()



@router.post(
    "/match",
    response_model=JDMatchReport,
    status_code=status.HTTP_200_OK,
    summary="Match CV against Job Description & Generate ATS Report",
    description="Accepts candidate ID and JD content (via pasted text or in-memory file upload), computes 50/30/20 ATS score, and returns localized Vietnamese report.",
    dependencies=[Depends(ats_rate_limiter)],
)
async def match_jd(
    candidate_id: str = Form(..., description="Candidate UUIDv7 ID in database"),
    jd_text: str | None = Form(None, description="Raw JD text content (up to 10,000 chars)"),
    jd_file: UploadFile | None = File(None, description="Optional JD file (PDF or DOCX, max 2MB)"),
    jd_parser: JDParser = Depends(get_cached_jd_parser),
    ats_matcher: ATSMatcher = Depends(get_cached_ats_matcher),
):
    """Conduct 3-pillar ATS compatibility evaluation between CandidateProfile and target JD."""
    # 1. Verify candidate exists
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ ứng viên #{candidate_id}",
        )

    try:
        profile = CandidateProfile.model_validate_json(candidate["profile_json"])
    except Exception as e:
        logger.error("Failed to parse candidate profile JSON: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hồ sơ ứng viên trong cơ sở dữ liệu không hợp lệ.",
        )

    # 2. Extract & Parse JD (File priority, then Text)
    jd_profile: JDProfile
    if jd_file and jd_file.filename:
        ext = Path(jd_file.filename).suffix.lower()
        if ext not in ALLOWED_JD_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ chấp nhận tệp JD định dạng PDF (.pdf) hoặc Microsoft Word (.docx).",
            )

        content = await jd_file.read()
        if len(content) > MAX_JD_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kích thước tệp JD ({len(content) / (1024*1024):.1f}MB) vượt quá giới hạn 2MB.",
            )

        try:
            jd_profile = await jd_parser.parse_jd_file(content, filename=jd_file.filename)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except Exception as e:
            logger.error("Error parsing JD file: %s", e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi trích xuất tệp JD. Vui lòng kiểm tra lại định dạng tệp hoặc thử lại sau.",
            )
    elif jd_text and jd_text.strip():
        cleaned_text = jd_text.strip()
        if len(cleaned_text) < 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nội dung mô tả công việc (JD) quá ngắn (tối thiểu 15 ký tự).",
            )
        try:
            jd_profile = await jd_parser.parse_jd_text(cleaned_text)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except Exception as e:
            logger.error("Error parsing JD text: %s", e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi phân tích nội dung JD. Vui lòng thử lại sau.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp nội dung mô tả công việc (JD) qua văn bản dán hoặc tải tệp PDF/Word.",
        )

    # 3. Match Profile against JD
    try:
        report = await ats_matcher.match(profile, jd_profile)
    except Exception as e:
        logger.error("Error during ATS matching: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi AI so khớp và chấm điểm ATS. Vui lòng thử lại sau.",
        )

    # 4. Save analysis to Database
    try:
        await save_analysis(
            candidate_id=candidate_id,
            ats_score=report.overall_score,
            ats_grade=report.overall_grade,
            report_json=report.model_dump_json(),
        )
    except Exception as db_err:
        logger.warning("Could not persist ATS analysis to database: %s", db_err)

    return report


@router.post(
    "/rewrite-star",
    response_model=STARResult,
    status_code=status.HTTP_200_OK,
    summary="Rewrite Bullet Point or Missing Skill to STAR Format",
    description="Accepts a raw bullet point or missing skill name and generates two high-impact STAR versions in Vietnamese.",
    dependencies=[Depends(star_rate_limiter)],
)
async def rewrite_bullet_to_star(
    payload: STARRewriteRequest,
    star_rewriter: STARRewriter = Depends(get_cached_star_rewriter),
):
    """Transform weak CV bullet points or missing skills into STAR format with power verbs and metrics."""
    try:
        return await star_rewriter.rewrite(
            raw_input=payload.raw_input,
            target_role=payload.target_role,
            context=payload.context,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error("Error during STAR rewrite: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi viết lại câu theo chuẩn STAR. Vui lòng thử lại sau.",
        )


@router.get(
    "/history/{candidate_id}",
    response_model=list[ATSHistoryItem],
    summary="Get ATS Analysis History for Candidate",
    dependencies=[Depends(read_rate_limiter)],
)
async def get_ats_history(candidate_id: str):
    """Retrieve historical ATS reports for a given candidate profile."""
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ ứng viên #{candidate_id}",
        )

    records = await get_candidate_analyses(candidate_id)
    return [
        ATSHistoryItem(
            id=r["id"],
            candidate_id=r["candidate_id"],
            ats_score=r["ats_score"],
            ats_grade=r["ats_grade"],
            report_json=r["report_json"],
            created_at=r.get("created_at"),
        )
        for r in records
    ]


@router.post(
    "/generate-cv",
    status_code=status.HTTP_200_OK,
    summary="Generate 1-Page Tailored Harvard CV in PDF Format",
    description="Synthesizes CandidateProfile and target JD into a tailored, single-page Harvard CV, returning a pure PDF stream.",
    dependencies=[Depends(cv_generation_rate_limiter)],
)
async def generate_harvard_cv(
    payload: GenerateCVRequest,
    jd_parser: JDParser = Depends(get_cached_jd_parser),
    ats_matcher: ATSMatcher = Depends(get_cached_ats_matcher),
    synthesizer: HarvardCVSynthesizer = Depends(get_cached_harvard_synthesizer),
):
    """Generate a single-page Harvard CV tailored to a Job Description in PDF binary format."""
    # 1. Verify candidate exists
    candidate = await get_candidate(payload.candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hồ sơ ứng viên #{payload.candidate_id}",
        )

    try:
        profile = CandidateProfile.model_validate_json(candidate["profile_json"])
    except Exception as e:
        logger.error("Failed to parse candidate profile JSON: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hồ sơ ứng viên trong cơ sở dữ liệu không hợp lệ.",
        )

    # 2. Parse JD
    cleaned_text = payload.jd_text.strip()
    if len(cleaned_text) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung mô tả công việc (JD) quá ngắn (tối thiểu 15 ký tự).",
        )

    try:
        jd_profile = await jd_parser.parse_jd_text(cleaned_text)
    except Exception as e:
        logger.error("Error parsing JD text: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích nội dung JD. Vui lòng thử lại sau.",
        )

    # 3. Match profile against JD for scoring and keyword targeting
    try:
        match_report = await ats_matcher.match(profile, jd_profile)
    except Exception as e:
        logger.error("Error during ATS matching: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi đánh giá mức độ tương thích ATS. Vui lòng thử lại sau.",
        )

    # 4. Synthesize Harvard CV with Critic-Actor Self-Reflection Loop
    target_lang = payload.language
    try:
        cv_data, reflection_result = await synthesizer.synthesize(
            profile=profile,
            jd=jd_profile,
            report=match_report,
            target_language=target_lang,
        )
    except Exception as e:
        logger.error("Error during Harvard CV synthesis: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi AI tổng hợp dữ liệu CV chuẩn Harvard. Vui lòng thử lại sau.",
        )

    # 5. Render PDF with Selected Template
    try:
        renderer_cls = get_cv_renderer(payload.template)
        pdf_bytes = renderer_cls.render(cv_data)
    except Exception as e:
        logger.error("Error rendering CV (%s): %s", payload.template, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất tệp PDF CV. Vui lòng thử lại sau.",
        )

    # Sanitize filename to ASCII for safe HTTP header transmission
    raw_name = profile.personal_info.full_name or "Candidate"
    ascii_name = unicodedata.normalize("NFKD", raw_name).encode("ascii", "ignore").decode("ascii")
    safe_name = re.sub(r"[^\w\-_]", "_", ascii_name).strip("_") or "Candidate"
    
    prefix_map = {
        "harvard": "Harvard_CV",
        "modern_tech": "ModernTech_CV",
        "executive": "Executive_CV",
    }
    prefix = prefix_map.get(payload.template, "Harvard_CV")
    filename = f"{prefix}_{safe_name}_{target_lang}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Estimated-ATS-Score": str(cv_data.ats_score_estimate),
            "X-Estimated-Word-Count": str(cv_data.estimated_word_count),
            "X-Critic-Score": str(reflection_result.final_critic_score),
            "X-Critic-Approved": str(reflection_result.is_converged).lower(),
            "X-Reflection-Iterations": str(reflection_result.iterations_count),
            "X-CV-Template": payload.template,
        },
    )


