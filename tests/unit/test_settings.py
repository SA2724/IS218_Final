# tests/unity/test_settings.py

import pytest
from app.settings import Settings

def test_load_env_settings():
    """
    Test that TestSettings correctly loads environment variables from .env.test
    """
    settings = Settings()

    assert settings.db_host == "localhost"
    assert settings.db_user == "postgres"
    assert settings.db_password == "Asqw12zx!@"
    assert settings.db_name == "fastapi_db"
    assert settings.db_port == 5432
    assert settings.salt == "aafasdfsdfsdfasdf"
    assert settings.api_key == "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"
