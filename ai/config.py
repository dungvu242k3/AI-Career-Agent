"""Typed AI configuration view backed by :mod:`be.config`.

Environment variables are parsed once by ``be.config.Settings``. Keeping the
AI package as a view over that object prevents workers and HTTP routes from
silently selecting different models for the same operation.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr

from be.config import get_settings


class AIConfig(BaseModel):
    """Canonical, typed view of the backend AI settings."""

    ai_provider: Literal["openai", "gemini"] = "openai"
    enable_fallback: bool = True

    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_extraction_model: str = "gpt-4o-mini"
    openai_reasoning_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    gemini_api_key: SecretStr = Field(default=SecretStr(""))
    gemini_flash_lite_model: str = "gemini-2.0-flash"
    gemini_flash_model: str = "gemini-2.5-flash-preview-05-20"

    extraction_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    extraction_max_tokens: int = Field(default=3_000, gt=0, le=8_192)
    reasoning_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reasoning_max_tokens: int = Field(default=3_000, gt=0, le=8_192)

    max_pdf_pages: int = Field(default=2, gt=0, le=20)
    max_file_size_mb: int = Field(default=2, gt=0, le=50)
    min_text_length: int = Field(default=50, gt=0)
    ai_daily_token_limit: int = Field(default=250_000, gt=0)
    ai_daily_cost_limit_usd: float = Field(default=5.0, gt=0)
    prompts_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent / "prompts")

    def get_openai_key(self) -> str:
        return self.openai_api_key.get_secret_value()

    def get_gemini_key(self) -> str:
        return self.gemini_api_key.get_secret_value()

    def model_for(
        self,
        stage: Literal["extraction", "analysis", "generation", "interview"],
        provider: Literal["openai", "gemini"],
    ) -> str:
        if provider == "openai":
            return self.openai_extraction_model if stage == "extraction" else self.openai_reasoning_model
        return self.gemini_flash_lite_model if stage == "extraction" else self.gemini_flash_model

    def validate_runtime(self) -> None:
        get_settings().validate_ai_settings(require_credentials=False)


@lru_cache
def get_ai_config() -> AIConfig:
    settings = get_settings()
    config = AIConfig.model_validate(settings.model_dump())
    config.validate_runtime()
    return config
