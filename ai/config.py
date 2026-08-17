"""AI Module Configuration — Model identifiers, inference parameters, and prompts."""

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class AIConfig(BaseSettings):
    # Gemini API Credentials
    gemini_api_key: str = ""

    # Primary Models
    extraction_model: str = "gemini-2.0-flash"
    reasoning_model: str = "gemini-2.5-flash-preview-05-20"

    # Extraction Hyperparameters
    extraction_temperature: float = 0.1
    extraction_max_tokens: int = 8192

    # Reasoning / ATS Hyperparameters
    reasoning_temperature: float = 0.3
    reasoning_max_tokens: int = 8192
    thinking_budget: int = 2048

    # Constraints & Limits
    max_pdf_pages: int = 5
    max_file_size_mb: int = 10
    min_text_length: int = 50

    # Paths
    prompts_dir: Path = Path(__file__).parent / "prompts"

    model_config = {
        "env_file": (".env", "be/.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_ai_config() -> AIConfig:
    return AIConfig()
