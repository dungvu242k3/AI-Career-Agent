"""Tests for Multi-Channel Job Aggregator & Domain Filtering."""

import pytest
from be.core.job_search import (
    detect_candidate_domain,
    get_job_by_id,
    search_jobs,
)


def test_detect_candidate_domain():
    """Test domain detection from job titles and skill sets."""
    assert detect_candidate_domain("Senior Backend Developer") == "backend"
    assert detect_candidate_domain("Frontend React Engineer") == "frontend"
    assert detect_candidate_domain("Fullstack Software Developer") == "fullstack"
    assert detect_candidate_domain("DevOps / Cloud Engineer") == "devops"
    assert detect_candidate_domain("iOS & Android Flutter Developer") == "mobile"
    assert detect_candidate_domain("AI Researcher / ML Engineer") == "ai_data"
    assert detect_candidate_domain(None, ["Python", "FastAPI", "SQL"]) == "backend"


def test_search_jobs_by_domain():
    """Test filtering jobs strictly by candidate domain."""
    be_jobs = search_jobs(domain="backend")
    assert len(be_jobs) > 0
    assert all(j.domain == "backend" or "backend" in j.domain for j in be_jobs)

    fe_jobs = search_jobs(domain="frontend")
    assert len(fe_jobs) > 0
    assert all(j.domain == "frontend" or "frontend" in j.domain for j in fe_jobs)


def test_search_jobs_by_platform():
    """Test filtering jobs by platform (ITviec, TopCV, LinkedIn, VietnamWorks)."""
    itviec_jobs = search_jobs(platform="ITviec")
    assert len(itviec_jobs) > 0
    assert all(j.platform.lower() == "itviec" for j in itviec_jobs)

    topcv_jobs = search_jobs(platform="TopCV")
    assert len(topcv_jobs) > 0
    assert all(j.platform.lower() == "topcv" for j in topcv_jobs)


def test_search_jobs_by_experience_level():
    """Test filtering jobs with candidate experience years."""
    mid_jobs = search_jobs(domain="backend", min_exp_years=3.0)
    assert len(mid_jobs) > 0
    # Every matched job must accommodate 3.0 years
    for j in mid_jobs:
        assert j.min_years_exp <= 5.0


def test_get_job_by_id():
    """Test retrieving full detailed job info."""
    job = get_job_by_id("job-be-001")
    assert job is not None
    assert job.title == "Senior Backend Engineer (Python / FastAPI / Async)"
    assert job.company == "VNG Corporation"
    assert len(job.requirements) > 20
    assert len(job.description) > 20
    assert "https://" in job.job_url

    non_existent = get_job_by_id("job-invalid-999")
    assert non_existent is None
