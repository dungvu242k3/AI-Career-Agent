import pytest

from be.config import Settings


def test_production_disallows_startup_database_ddl():
    settings = Settings(
        _env_file=None, app_env="production", database_auto_migrate=True
    )

    with pytest.raises(RuntimeError, match="DATABASE_AUTO_MIGRATE"):
        settings.validate_production_settings()
