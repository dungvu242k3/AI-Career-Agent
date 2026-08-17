"""CareerPilot AI — Backend Configuration."""

from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Production-ready Backend configuration."""

    # App Settings
    app_name: str = Field(default="CareerPilot AI")
    debug: bool = Field(default=False, description="Debug mode flag — disabled by default in prod")
    api_prefix: str = Field(default="/api/v1")

    # Database (PostgreSQL default connection URL)
    # Examples:
    # - Local: postgresql+asyncpg://postgres:password@localhost:5432/careerpilot
    # - Supabase / Neon: postgresql+asyncpg://user:pass@ep-xyz.aws.neon.tech/careerpilot?ssl=require
    # - SQLite fallback: sqlite+aiosqlite:///./data/careerpilot.db
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/careerpilot",
        description="Async database connection URL (PostgreSQL / SQLite)",
    )
    db_path: Path = Field(default=WORKSPACE_ROOT / "data" / "careerpilot.db")

    # Gemini AI Credentials & Models
    gemini_api_key: SecretStr = Field(default=SecretStr(""))
    gemini_flash_model: str = Field(default="gemini-2.5-flash-preview-05-20")
    gemini_flash_lite_model: str = Field(default="gemini-2.0-flash")

    # OpenAI AI Credentials & Models
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_extraction_model: str = Field(default="gpt-4o-mini")
    openai_reasoning_model: str = Field(default="gpt-4o")

    # Uploads
    upload_dir: Path = Field(default=WORKSPACE_ROOT / "data" / "uploads")
    max_upload_size_mb: int = Field(default=10, gt=0, le=50)

    # Security & CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    model_config = {
        "env_file": (".env", "be/.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_api_key_value(self) -> str:
        return self.gemini_api_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
