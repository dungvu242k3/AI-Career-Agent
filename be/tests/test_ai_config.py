import pytest

from be.config import Settings


def test_ai_configuration_rejects_missing_model_name_at_startup():
    settings = Settings(_env_file=None, openai_extraction_model="  ")

    with pytest.raises(RuntimeError, match="OpenAI extraction"):
        settings.validate_ai_settings()


def test_production_requires_primary_and_enabled_fallback_credentials(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "rediss://redis.example/0")
    settings = Settings(
        _env_file=None,
        app_env="production",
        database_url="postgresql+asyncpg://app:secret@db.example/careerpilot?ssl=require",
        storage_backend="minio",
        minio_secure=True,
        minio_access_key="not-default",
        minio_secret_key="not-default-password",
        jwt_secret="a" * 64,
        cors_origins=["https://app.example"],
        ai_provider="openai",
        openai_api_key="primary-key",
        gemini_api_key="",
        enable_fallback=True,
    )

    with pytest.raises(RuntimeError, match="Fallback is enabled"):
        settings.validate_production_settings()
