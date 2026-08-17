"""CareerPilot AI — Backend Configuration"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "CareerPilot AI"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # Gemini
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash-preview-05-20"
    gemini_flash_lite_model: str = "gemini-2.0-flash"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/careerpilot.db"

    # Upload
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 10

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
