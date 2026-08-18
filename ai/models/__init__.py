"""Canonical domain models for AI processing."""

from ai.models.candidate import CandidateProfile
from ai.models.analysis import AnalysisReport
from ai.models.jd import JDProfile, JDMatchReport, SkillMatchItem
from ai.models.star import STARResult
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardContactInfo,
    HarvardEducationItem,
    HarvardExperienceItem,
    HarvardProjectItem,
    HarvardSkillsCategory,
    HarvardCertAndLangSection,
)

__all__ = [
    "CandidateProfile",
    "AnalysisReport",
    "JDProfile",
    "JDMatchReport",
    "SkillMatchItem",
    "STARResult",
    "HarvardCVData",
    "HarvardContactInfo",
    "HarvardEducationItem",
    "HarvardExperienceItem",
    "HarvardProjectItem",
    "HarvardSkillsCategory",
    "HarvardCertAndLangSection",
]

