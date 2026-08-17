"""Abstract Base Profile Extractor Interface."""

from abc import ABC, abstractmethod
from ai.models.candidate import CandidateProfile


class BaseProfileExtractor(ABC):
    """Interface for converting raw unstructured text into structured CandidateProfile."""

    @abstractmethod
    async def extract_profile(self, raw_text: str) -> CandidateProfile:
        """Extract structured candidate profile from text."""
        pass
