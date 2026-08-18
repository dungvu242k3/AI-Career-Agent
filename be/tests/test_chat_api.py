"""API tests for Chat & Job Search endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from be.main import app


@pytest.mark.asyncio
async def test_chat_job_search_intent():
    """Test sending a job search query returns job cards."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/message",
            json={"message": "Tìm việc làm backend 3 năm kinh nghiệm ở TP.HCM"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_intent"] == "job_search"
        assert len(data["jobs_found"]) > 0
        
        first_job = data["jobs_found"][0]
        assert "title" in first_job
        assert "company" in first_job
        assert "platform" in first_job
        assert "experience_required" in first_job
        assert "job_url" in first_job
        assert "description" in first_job


@pytest.mark.asyncio
async def test_chat_general_advice():
    """Test general career question returns advice."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/message",
            json={"message": "Làm thế nào để viết tóm tắt CV hay?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_intent"] == "cv_advice"
        assert len(data["reply"]) > 20


@pytest.mark.asyncio
async def test_get_jobs_by_domain_endpoint():
    """Test GET /api/v1/jobs/by-domain."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/by-domain?domain=frontend")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "frontend"
        assert data["total"] > 0
        assert len(data["jobs"]) > 0


@pytest.mark.asyncio
async def test_get_job_details_endpoint():
    """Test GET /api/v1/jobs/{job_id}."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/job-be-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "job-be-001"
        assert data["company"] == "VNG Corporation"

        # Not found case
        not_found = await client.get("/api/v1/jobs/non-existent-id")
        assert not_found.status_code == 404
