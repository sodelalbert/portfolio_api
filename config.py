from typing import Optional
from pydantic import field_validator

from pydantic_settings import BaseSettings
from sqlmodel import Field


class Settings(BaseSettings):
    """
    Settings for the Portfolio API.
    """

    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str = ""
    ALLOWED_ORIGINS: str = ""
    DEBUG: Optional[bool] = False

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("DATABASE_URL cannot be empty in .env file")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
