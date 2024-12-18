# tests/unit/test_settings.py

import pytest
from app.settings import TestSettings

def test_load_env_settings(test_settings: TestSettings):
    """
    Test that TestSettings correctly loads environment variables from .env.test
    """
    assert test_settings.db_host == "localhost"
    assert test_settings.db_user == "postgres"
    assert test_settings.db_password == "Asqw12zx!"
    assert test_settings.db_name == "fastapi_db"
    assert test_settings.db_port == 5432
    assert test_settings.salt == "aafasdfsdfsdfasdf"
    assert test_settings.api_key == "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"
