# app/settings.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class Settings(BaseSettings):
    db_host: str
    db_user: str
    db_password: str
    db_name: str
    db_port: int
    salt: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

class TestSettings(Settings):
    api_key: str = Field(..., alias="API_KEY")  # Explicitly map API_KEY

    model_config = ConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="forbid"  # Disallow extra fields
    )
