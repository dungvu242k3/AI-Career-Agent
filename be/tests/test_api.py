"""Integration tests for Backend API routes and Security Hardening."""

import uuid
import pytest
from fastapi.testclient import TestClient
from ai.models.candidate import CandidateProfile, PersonalInfo, SkillsTaxonomy, SummarySection
from ai.pipeline import CVIngestionPipeline
from be.main import app
from be.api.v1.cv_router import get_cached_ingestion_pipeline, sanitize_filename


class MockPipeline(CVIngestionPipeline):
    async def process_bytes(self, content_bytes: bytes, filename: str = "upload.pdf") -> tuple[str, CandidateProfile]:
        return "Sample raw CV text", CandidateProfile(
            personal_info=PersonalInfo(full_name="Le Van Test", email="test@example.com"),
            summary=SummarySection(detected_title="QA Engineer"),
            skills_taxonomy=SkillsTaxonomy(programming_languages=["Python"]),
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_cached_ingestion_pipeline] = lambda: MockPipeline()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check_and_security_headers(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    # Verify OWASP Security Headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_filename_sanitization_path_traversal():
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("..\\..\\windows\\system32\\calc.pdf") == "calc.pdf"
    assert sanitize_filename("my resume (1).pdf") == "my_resume__1_.pdf"
    assert sanitize_filename(".hidden.pdf").endswith(".pdf")
    assert not sanitize_filename(".hidden.pdf").startswith(".")


def test_upload_non_pdf_rejected(client):
    response = client.post(
        "/api/v1/cv/upload",
        files={"file": ("test.txt", b"plain text", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_upload_success_and_preview_workflow(client):
    # Use unique bytes to avoid colliding with cached test runs
    unique_token = uuid.uuid4().hex.encode()
    dummy_pdf_bytes = b"%PDF-1.4 " + unique_token + b" dummy pdf content"

    # 1. Upload
    response = client.post(
        "/api/v1/cv/upload",
        files={"file": ("my_cv.pdf", dummy_pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert "candidate_id" in data
    candidate_id = data["candidate_id"]
    assert data["profile"]["personal_info"]["full_name"] == "Le Van Test"
    assert data["is_cached"] is False

    # 2. Get Preview
    preview_res = client.get(f"/api/v1/cv/preview/{candidate_id}")
    assert preview_res.status_code == 200
    assert preview_res.json()["personal_info"]["full_name"] == "Le Van Test"

    # 3. Update Preview
    updated_profile = preview_res.json()
    updated_profile["personal_info"]["full_name"] = "Le Van Updated"
    update_res = client.put(
        f"/api/v1/cv/preview/{candidate_id}",
        json={"profile": updated_profile},
    )
    assert update_res.status_code == 200

    # 4. Verify Update persisted
    recheck_res = client.get(f"/api/v1/cv/preview/{candidate_id}")
    assert recheck_res.status_code == 200
    assert recheck_res.json()["personal_info"]["full_name"] == "Le Van Updated"
