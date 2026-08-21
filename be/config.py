"""CareerPilot AI — Backend Configuration."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Production-ready Backend configuration."""

    # App Settings
    app_name: str = Field(default="CareerPilot AI")
    app_env: str = Field(default="development", validation_alias=AliasChoices("APP_ENV", "CAREERPILOT_ENV"))
    debug: bool = Field(default=False, validation_alias=AliasChoices("CAREERPILOT_DEBUG", "DEBUG"))
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
    database_auto_migrate: bool = Field(
        default=False,
        validation_alias=AliasChoices("DATABASE_AUTO_MIGRATE"),
        description="Allow startup DDL outside production; production requires explicit migrations",
    )
    db_path: Path = Field(default=WORKSPACE_ROOT / "data" / "careerpilot.db")

    # AI routing.  This Settings object is the canonical source for both
    # FastAPI and the ``ai`` package.
    ai_provider: Literal["openai", "gemini"] = Field(default="openai")
    enable_fallback: bool = Field(default=True)

    # Gemini AI Credentials & Models
    gemini_api_key: SecretStr = Field(default=SecretStr(""))
    gemini_flash_model: str = Field(default="gemini-2.5-flash-preview-05-20")
    gemini_flash_lite_model: str = Field(default="gemini-2.0-flash")

    # OpenAI AI Credentials & Models
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_extraction_model: str = Field(default="gpt-4o-mini")
    openai_reasoning_model: str = Field(default="gpt-4o")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    extraction_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    extraction_max_tokens: int = Field(default=3_000, gt=0, le=8_192)
    reasoning_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    reasoning_max_tokens: int = Field(default=3_000, gt=0, le=8_192)
    max_pdf_pages: int = Field(default=2, gt=0, le=20)
    min_text_length: int = Field(default=50, gt=0)
    ai_cache_hmac_secret: SecretStr = Field(default=SecretStr(""))
    ai_daily_token_limit: int = Field(default=250_000, gt=0)
    ai_daily_cost_limit_usd: float = Field(default=5.0, gt=0)

    # Uploads & Object Storage (MinIO / S3 / Local)
    storage_backend: str = Field(default="minio", description="Storage provider: 'minio' or 'local'")
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO S3 endpoint (host:port)")
    minio_access_key: SecretStr = Field(default=SecretStr(""))
    minio_secret_key: SecretStr = Field(default=SecretStr(""))
    minio_bucket: str = Field(default="careerpilot-cvs")
    minio_secure: bool = Field(default=False, description="Use SSL/TLS (HTTPS) for MinIO connection")
    upload_dir: Path = Field(default=WORKSPACE_ROOT / "data" / "uploads")
    max_upload_size_mb: int = Field(default=2, gt=0, le=50)


    # Security, Auth & CORS
    jwt_secret: SecretStr = Field(
        default=SecretStr(""),
        description="Shared secret key for signing and verifying JWT tokens",
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_issuer: str = Field(default="careerpilot-auth")
    jwt_audience: str = Field(default="careerpilot-api")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    model_config = {
        "env_file": (".env", "be/.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_value(cls, value: object) -> object:
        """Treat common deployment labels as debug disabled, not invalid booleans."""
        if isinstance(value, str) and value.strip().lower() in {"release", "production"}:
            return False
        return value

    def get_api_key_value(self) -> str:
        return self.gemini_api_key.get_secret_value()

    def get_jwt_secret_value(self) -> str:
        import os
        return self.jwt_secret.get_secret_value() or os.getenv("JWT_SECRET", "")

    def get_minio_access_key(self) -> str:
        import os
        return self.minio_access_key.get_secret_value() or os.getenv("MINIO_ACCESS_KEY", "minioadmin")

    def get_minio_secret_key(self) -> str:
        import os
        return self.minio_secret_key.get_secret_value() or os.getenv("MINIO_SECRET_KEY", "minioadmin")
    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def validate_production_settings(self) -> None:
        import os
        if not self.is_production:
            return
        if self.database_auto_migrate:
            raise RuntimeError(
                "DATABASE_AUTO_MIGRATE must be false in production; run migrations explicitly"
            )
        if self.debug:
            raise RuntimeError("DEBUG must be false in production")
        if not self.database_url.startswith(("postgres://", "postgresql://", "postgresql+asyncpg://")):
            raise RuntimeError("PostgreSQL is required in production")
        if "ssl=" not in self.database_url.lower() and "sslmode=" not in self.database_url.lower():
            raise RuntimeError("TLS must be required for PostgreSQL in production")
        if self.storage_backend != "minio" or not self.minio_secure:
            raise RuntimeError("TLS-enabled object storage is required in production")
        if not self.get_jwt_secret_value() or len(self.get_jwt_secret_value()) < 32:
            raise RuntimeError("A JWT_SECRET of at least 32 characters is required in production")
        if self.get_minio_access_key() == "minioadmin" or self.get_minio_secret_key() == "minioadminpassword":
            raise RuntimeError("Default MinIO credentials are forbidden in production")
        redis_url = os.getenv("REDIS_URL", "")
        if not redis_url.startswith("rediss://"):
            raise RuntimeError("A TLS-enabled REDIS_URL is required in production")
        if not self.cors_origins or any(origin == "*" or "localhost" in origin for origin in self.cors_origins):
            raise RuntimeError("Explicit non-localhost CORS origins are required in production")
        self.validate_ai_settings(require_credentials=True)

    def validate_ai_settings(self, *, require_credentials: bool = False) -> None:
        """Validate model routing once, before a request reaches a provider."""
        if not self.openai_extraction_model.strip() or not self.openai_reasoning_model.strip():
            raise RuntimeError("OpenAI extraction and reasoning model names must be configured")
        if not self.gemini_flash_lite_model.strip() or not self.gemini_flash_model.strip():
            raise RuntimeError("Gemini extraction and reasoning model names must be configured")

        if not require_credentials:
            return
        primary_key = (
            self.openai_api_key.get_secret_value()
            if self.ai_provider == "openai"
            else self.gemini_api_key.get_secret_value()
        )
        if not primary_key.strip():
            raise RuntimeError(f"{self.ai_provider.upper()} API key is required in production")
        if self.enable_fallback:
            fallback_key = (
                self.gemini_api_key.get_secret_value()
                if self.ai_provider == "openai"
                else self.openai_api_key.get_secret_value()
            )
            if not fallback_key.strip():
                raise RuntimeError("Fallback is enabled but the secondary AI provider key is missing")


@lru_cache
def get_settings() -> Settings:
    return Settings()
