"""CareerPilot AI — Core AI Package (ai).

Clean, modular, SOLID-compliant AI engine for document parsing,
structured extraction, ATS scoring, and agent orchestration.
"""

from ai.models.candidate import CandidateProfile
from ai.pipeline import CVIngestionPipeline, get_default_ingestion_pipeline

__all__ = [
    "CandidateProfile",
    "CVIngestionPipeline",
    "get_default_ingestion_pipeline",
]
