"""Integration tests for ATS Matching, STAR Rewriter, and Analysis History API endpoints."""

import json
import pytest
from fastapi.testclient import TestClient

from ai.analysis.ats_matcher import ATSMatcher
from ai.analysis.star_rewriter import STARRewriter
from ai.models.candidate import CandidateProfile, PersonalInfo, SkillsTaxonomy, SummarySection
from ai.models.jd import JDMatchReport, JDProfile, SkillMatchItem
from ai.models.star import STARResult
from ai.parsers.jd_parser import JDParser
from be.api.v1.ats_router import (
    get_cached_ats_matcher,
    get_cached_jd_parser,
    get_cached_star_rewriter,
)
from be.db.database import save_candidate
from be.main import app


class MockJDParser(JDParser):
    async def parse_jd_text(self, raw_text: str) -> JDProfile:
        return JDProfile(
            job_title="Senior Python Engineer",
            must_have_skills=["Python", "FastAPI"],
            nice_to_have_skills=["Redis"],
            min_experience_years=3,
            raw_text=raw_text,
        )

    async def parse_jd_file(self, content_bytes: bytes, filename: str) -> JDProfile:
        return await self.parse_jd_text("Sample extracted JD text from file")


class MockATSMatcher(ATSMatcher):
    async def match(self, profile: CandidateProfile, jd: JDProfile) -> JDMatchReport:
        return JDMatchReport(
            overall_score=85,
            skill_match_score=90,
            experience_fit_score=80,
            format_quality_score=75,
            matched_skills=[
                SkillMatchItem(
                    skill_name="Python",
                    match_type="exact",
                    cv_evidence="Python listed",
                    jd_requirement="Python required",
                    importance="required",
                )
            ],
            missing_skills=[
                SkillMatchItem(
                    skill_name="Redis",
                    match_type="missing",
                    cv_evidence=None,
                    jd_requirement="Redis preferred",
                    importance="preferred",
                )
            ],
            top_recommendations=["Bổ sung Redis", "Thêm số liệu định lượng"],
            experience_gap_analysis="Ứng viên đáp ứng tốt yêu cầu.",
            jd_title=jd.job_title,
        )


class MockSTARRewriter(STARRewriter):
    async def rewrite(
        self, raw_input: str, target_role: str = "Software Engineer", context: str | None = None
    ) -> STARResult:
        return STARResult(
            original=raw_input,
            star_v1=f"Xây dựng tính năng liên quan đến {raw_input} phục vụ 50,000 người dùng.",
            star_v2=f"Kiến trúc giải pháp {raw_input} tối ưu 40% chi phí hạ tầng.",
            action_verb="Kiến trúc",
            improvements=["Thêm số liệu", "Sử dụng động từ hành động mạnh"],
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_cached_jd_parser] = lambda: MockJDParser()
    app.dependency_overrides[get_cached_ats_matcher] = lambda: MockATSMatcher()
    app.dependency_overrides[get_cached_star_rewriter] = lambda: MockSTARRewriter()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


import pytest_asyncio

@pytest_asyncio.fixture
async def sample_candidate_id():
    profile = CandidateProfile(
        personal_info=PersonalInfo(full_name="Trần Thị B", email="b.tran@example.com"),
        summary=SummarySection(detected_title="Senior Developer"),
        skills_taxonomy=SkillsTaxonomy(programming_languages=["Python", "FastAPI"]),
    )
    return await save_candidate(
        profile_json=profile.model_dump_json(),
        full_name="Trần Thị B",
        email="b.tran@example.com",
        title="Senior Developer",
    )


@pytest.mark.asyncio
async def test_match_candidate_not_found_returns_404(client):
    response = client.post(
        "/api/v1/ats/match",
        data={"candidate_id": 999999, "jd_text": "Tuyển dụng kỹ sư Backend Python 3 năm kinh nghiệm"},
    )
    assert response.status_code == 404
    assert "Không tìm thấy" in response.json()["detail"]


@pytest.mark.asyncio
async def test_match_empty_jd_returns_400(client, sample_candidate_id):
    cid = sample_candidate_id
    response = client.post(
        "/api/v1/ats/match",
        data={"candidate_id": cid},
    )
    assert response.status_code == 400
    assert "Vui lòng cung cấp" in response.json()["detail"]


@pytest.mark.asyncio
async def test_match_short_jd_text_returns_400(client, sample_candidate_id):
    cid = sample_candidate_id
    response = client.post(
        "/api/v1/ats/match",
        data={"candidate_id": cid, "jd_text": "short"},
    )
    assert response.status_code == 400
    assert "quá ngắn" in response.json()["detail"]


@pytest.mark.asyncio
async def test_match_unsupported_jd_file_ext_returns_400(client, sample_candidate_id):
    cid = sample_candidate_id
    response = client.post(
        "/api/v1/ats/match",
        data={"candidate_id": cid},
        files={"jd_file": ("job.txt", b"plain text jd", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"] or "Word" in response.json()["detail"]


@pytest.mark.asyncio
async def test_match_with_jd_text_success(client, sample_candidate_id):
    cid = sample_candidate_id
    response = client.post(
        "/api/v1/ats/match",
        data={
            "candidate_id": cid,
            "jd_text": "Tuyển dụng Senior Python Backend Engineer yêu cầu thành thạo FastAPI và PostgreSQL",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 85
    assert data["overall_grade"] == "A"
    assert "Phù hợp tốt" in data["verdict"]
    assert len(data["matched_skills"]) == 1
    assert len(data["missing_skills"]) == 1
    assert data["jd_title"] == "Senior Python Engineer"


@pytest.mark.asyncio
async def test_match_with_jd_file_pdf_success(client, sample_candidate_id):
    cid = sample_candidate_id
    response = client.post(
        "/api/v1/ats/match",
        data={"candidate_id": cid},
        files={"jd_file": ("job_description.pdf", b"%PDF-1.4 dummy pdf bytes", "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 85
    assert data["overall_grade"] == "A"


@pytest.mark.asyncio
async def test_match_with_jd_file_docx_success(client, sample_candidate_id):
    cid = sample_candidate_id
    response = client.post(
        "/api/v1/ats/match",
        data={"candidate_id": cid},
        files={"jd_file": ("job_description.docx", b"\x50\x4B\x03\x04 dummy docx bytes", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 85


def test_rewrite_star_success(client):
    response = client.post(
        "/api/v1/ats/rewrite-star",
        json={"raw_input": "Redis", "target_role": "Senior Backend Engineer"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "Redis"
    assert "Redis" in data["star_v1"]
    assert data["action_verb"] == "Kiến trúc"
    assert len(data["improvements"]) == 2


def test_rewrite_star_empty_input_returns_422_or_400(client):
    response = client.post(
        "/api/v1/ats/rewrite-star",
        json={"raw_input": "a", "target_role": "Backend"},
    )
    # pydantic min_length=2 triggers 422
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_get_ats_history_workflow(client, sample_candidate_id):
    cid = sample_candidate_id

    # 1. Perform match to create history entry
    client.post(
        "/api/v1/ats/match",
        data={"candidate_id": cid, "jd_text": "Tuyển dụng Backend Engineer kinh nghiệm 3 năm"},
    )

    # 2. Query history
    history_res = client.get(f"/api/v1/ats/history/{cid}")
    assert history_res.status_code == 200
    history_list = history_res.json()
    assert len(history_list) >= 1
    assert history_list[0]["candidate_id"] == cid
    assert history_list[0]["ats_score"] == 85
    assert history_list[0]["ats_grade"] == "A"


def test_get_ats_history_candidate_not_found_returns_404(client):
    response = client.get("/api/v1/ats/history/999999")
    assert response.status_code == 404
