"""ATS Router — API endpoints for Job Description matching, ATS compatibility scoring, and STAR rewriting."""

from functools import lru_cache
import logging
from pathlib import Path

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
)
from be.core.rate_limiter import (
    ats_rate_limiter,
    read_rate_limiter,
    star_rate_limiter,
)
from be.db.database import (
    get_candidate,
    get_candidate_analyses,
    save_analysis,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@lru_cache(maxsize=1)
def get_cached_jd_parser() -> JDParser:
    return get_default_jd_parser()


@lru_cache(maxsize=1)
def get_cached_ats_matcher() -> ATSMatcher:
    return get_default_ats_matcher()


@lru_cache(maxsize=1)
def get_cached_star_rewriter() -> STARRewriter:
    return get_default_star_rewriter()


@router.post(
    "/match",
    response_model=JDMatchReport,
    status_code=status.HTTP_200_OK,
    summary="Match CV against Job Description & Generate ATS Report",
    description="Accepts candidate ID and JD content (via pasted text or in-memory file upload), computes 50/30/20 ATS score, and returns localized Vietnamese report.",
    dependencies=[Depends(ats_rate_limiter)],
)
async def match_jd(
    candidate_id: int = Form(..., description="Candidate ID in database"),
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
async def get_ats_history(candidate_id: int):
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
