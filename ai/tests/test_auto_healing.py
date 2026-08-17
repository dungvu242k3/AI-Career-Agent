"""Unit tests for GeminiCVExtractor auto-healing and experience interval merging."""

import pytest
from unittest.mock import MagicMock
from ai.extractors.cv_extractor import GeminiCVExtractor
from ai.models.candidate import WorkExperienceItem


@pytest.fixture
def extractor():
    return GeminiCVExtractor()


def test_experience_estimation_merges_overlapping_intervals(extractor):
    # Two overlapping jobs:
    # Job 1: 2021-01 to 2022-12 (24 months)
    # Job 2: 2022-06 to 2023-06 (overlaps by 6 months, spans to 2023-06 -> total 30 months = 2.5 years)
    work_history = [
        WorkExperienceItem(company="A", role="Dev", start_date="2021-01", end_date="2022-12"),
        WorkExperienceItem(company="B", role="Lead", start_date="2022-06", end_date="2023-06"),
    ]
    years = extractor._estimate_total_experience(work_history)
    # 2021-01 to 2023-06 is 30 months / 12 = 2.5 years
    assert years == 2.5


def test_experience_estimation_handles_invalid_dates_gracefully(extractor):
    work_history = [
        WorkExperienceItem(company="X", role="Intern", start_date="invalid-date", end_date="2023"),
    ]
    years = extractor._estimate_total_experience(work_history)
    assert years == 0.0


def test_auto_heal_sanitizes_urls_and_deduplicates_skills(extractor):
    raw_data = {
        "personal_info": {
            "full_name": "Pham Van C",
            "linkedin_url": "linkedin.com/in/phamvanc",
            "github_url": "https://github.com/phamvanc",
            "phone": "+84 (090) 123-4567",
        },
        "skills_taxonomy": {
            "programming_languages": ["Python", "python", " PYTHON ", "Go"],
            "databases": ["PostgreSQL", "redis", "Redis"],
        },
        "projects": [
            {"name": "App", "url": "myproject.dev"},
        ],
    }

    profile = extractor._auto_heal_profile(raw_data)
    assert profile.personal_info.linkedin_url == "https://linkedin.com/in/phamvanc"
    assert profile.personal_info.github_url == "https://github.com/phamvanc"
    assert profile.skills_taxonomy.programming_languages == ["Python", "Go"]
    assert profile.skills_taxonomy.databases == ["PostgreSQL", "redis"]
    assert profile.projects[0].url == "https://myproject.dev"
