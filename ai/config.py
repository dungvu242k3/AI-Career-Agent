"""AI Module Configuration — Model identifiers, inference parameters, and prompts."""

from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    """Configuration for AI processing, models, and extraction limits."""

    # Gemini API Credentials (SecretStr protects against accidental logging)
    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="Google Gemini API key",
    )

    # Primary Models (Configurable via ENV)
    extraction_model: str = Field(
        default="gemini-2.0-flash",
        description="Primary model for structured extraction",
    )
    reasoning_model: str = Field(
        default="gemini-2.5-flash-preview-05-20",
        description="Reasoning model for ATS evaluation & STAR rewriter",
    )

    # Extraction Hyperparameters
    extraction_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    extraction_max_tokens: int = Field(default=8192, gt=0)

    # Reasoning / ATS Hyperparameters
    reasoning_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reasoning_max_tokens: int = Field(default=8192, gt=0)
    thinking_budget: int = Field(default=2048, ge=0)

    # Document Limits & Guardrails
    max_pdf_pages: int = Field(default=5, gt=0, le=20)
    max_file_size_mb: int = Field(default=10, gt=0, le=50)
    min_text_length: int = Field(default=50, gt=0)

    # Paths (Dynamically resolved relative to module)
    prompts_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "prompts"
    )

    model_config = {
        "env_file": (".env", "be/.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_api_key_value(self) -> str:
        """Helper to get unwrapped API key string."""
        return self.gemini_api_key.get_secret_value()


@lru_cache
def get_ai_config() -> AIConfig:
    """Cached singleton configuration."""
    return AIConfig()
