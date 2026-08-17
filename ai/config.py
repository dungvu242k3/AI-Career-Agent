"""AI Module Configuration — Multi-provider settings (OpenAI & Gemini), inference parameters, and prompts."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    """Configuration for AI processing across multiple LLM providers."""

    # Provider Selection
    ai_provider: Literal["openai", "gemini"] = Field(
        default="openai",
        description="Active LLM provider for extraction and analysis ('openai' or 'gemini')",
    )
    enable_fallback: bool = Field(
        default=True,
        description="Automatically fallback to secondary provider if primary fails",
    )

    # --- OPENAI CONFIGURATION (PRIMARY) ---
    openai_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="OpenAI API key (sk-proj-...)",
    )
    openai_extraction_model: str = Field(
        default="gpt-4o-mini",
        description="Model for fast, structured CV extraction",
    )
    openai_reasoning_model: str = Field(
        default="gpt-4o",
        description="Model for in-depth ATS scoring & STAR rewriter",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Model for vector embedding generation",
    )

    # --- GOOGLE GEMINI CONFIGURATION (SECONDARY / FALLBACK) ---
    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="Google Gemini API key",
    )
    gemini_flash_lite_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini extraction model",
    )
    gemini_flash_model: str = Field(
        default="gemini-2.5-flash-preview-05-20",
        description="Gemini reasoning model",
    )

    # Hyperparameters
    extraction_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    extraction_max_tokens: int = Field(default=8192, gt=0)
    reasoning_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reasoning_max_tokens: int = Field(default=8192, gt=0)

    # Document Limits & Guardrails
    max_pdf_pages: int = Field(default=5, gt=0, le=20)
    max_file_size_mb: int = Field(default=10, gt=0, le=50)
    min_text_length: int = Field(default=50, gt=0)

    # Paths
    prompts_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "prompts"
    )

    model_config = {
        "env_file": (".env", "be/.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_openai_key(self) -> str:
        return self.openai_api_key.get_secret_value()

    def get_gemini_key(self) -> str:
        return self.gemini_api_key.get_secret_value()


@lru_cache
def get_ai_config() -> AIConfig:
    return AIConfig()
