"""CV Router — API endpoints for CV upload, extraction, and analysis."""

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from config import get_settings
from services.pdf_parser import extract_text_from_bytes
from services.cv_extractor import extract_profile
from services.cv_analyzer import analyze_cv
from models.candidate import CandidateProfile
from models.analysis import AnalysisReport
from db.database import save_candidate, save_analysis, save_upload, get_candidate, get_analysis

router = APIRouter()


class UploadResponse(BaseModel):
    candidate_id: int
    filename: str
    text_length: int
    profile: CandidateProfile


class AnalyzeResponse(BaseModel):
    candidate_id: int
    report: AnalysisReport


class FullReportResponse(BaseModel):
    candidate_id: int
    profile: CandidateProfile
    report: AnalysisReport


@router.post("/upload", response_model=UploadResponse)
async def upload_cv(file: UploadFile = File(...)):
    """Upload a CV PDF file, extract text, and parse into structured profile.

    Returns the candidate ID and extracted profile.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Validate file size
    settings = get_settings()
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    # Save file to disk
    file_id = uuid.uuid4().hex[:8]
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{file_id}_{file.filename}"
    file_path.write_bytes(content)

    # Extract text from PDF
    try:
        raw_text = extract_text_from_bytes(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Extract structured profile using Gemini
    try:
        profile = await extract_profile(raw_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"CV extraction failed: {e}")

    # Save to database
    candidate_id = await save_candidate(
        profile_json=profile.model_dump_json(),
        full_name=profile.full_name,
        email=profile.email,
        title=profile.title,
    )
    await save_upload(
        filename=file.filename,
        file_path=str(file_path),
        raw_text=raw_text,
        candidate_id=candidate_id,
    )

    return UploadResponse(
        candidate_id=candidate_id,
        filename=file.filename,
        text_length=len(raw_text),
        profile=profile,
    )


@router.post("/analyze/{candidate_id}", response_model=AnalyzeResponse)
async def analyze_candidate(candidate_id: int):
    """Run ATS analysis on a previously uploaded CV.

    Returns the analysis report with scores and recommendations.
    """
    # Get candidate profile from DB
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    profile = CandidateProfile.model_validate_json(candidate["profile_json"])

    # Run analysis with Gemini
    try:
        report = await analyze_cv(profile)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"CV analysis failed: {e}")

    # Save analysis to DB
    await save_analysis(
        candidate_id=candidate_id,
        ats_score=report.ats_score,
        ats_grade=report.ats_grade,
        report_json=report.model_dump_json(),
    )

    return AnalyzeResponse(candidate_id=candidate_id, report=report)


@router.get("/report/{candidate_id}", response_model=FullReportResponse)
async def get_report(candidate_id: int):
    """Get the full report for a candidate (profile + latest analysis)."""
    candidate = await get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

    analysis = await get_analysis(candidate_id)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for candidate {candidate_id}. Run POST /analyze/{candidate_id} first.",
        )

    profile = CandidateProfile.model_validate_json(candidate["profile_json"])
    report = AnalysisReport.model_validate_json(analysis["report_json"])

    return FullReportResponse(
        candidate_id=candidate_id,
        profile=profile,
        report=report,
    )


@router.post("/upload-and-analyze", response_model=FullReportResponse)
async def upload_and_analyze(file: UploadFile = File(...)):
    """One-shot endpoint: Upload CV + Extract + Analyze in one call.

    Convenience endpoint that combines upload and analyze steps.
    """
    # Upload & extract
    upload_result = await upload_cv(file)

    # Analyze
    analyze_result = await analyze_candidate(upload_result.candidate_id)

    return FullReportResponse(
        candidate_id=upload_result.candidate_id,
        profile=upload_result.profile,
        report=analyze_result.report,
    )
