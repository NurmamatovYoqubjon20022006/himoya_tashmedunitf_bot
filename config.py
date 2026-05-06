"""Loyiha sozlamalari (pydantic-settings)."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str
    bot_username: str = "himoya_tashmedunitf_bot"

    admin_ids: Annotated[list[int], NoDecode] = Field(default_factory=list)

    database_url: str = "postgresql+asyncpg://postgres:CHANGE_ME@localhost:5432/himoya"
    database_sync_url: str = "postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/himoya"
    redis_url: str = ""

    environment: Literal["development", "production"] = "development"
    log_level: str = "INFO"

    encryption_key: str = ""

    rate_limit_seconds: int = 300
    default_language: Literal["uz", "ru", "en"] = "uz"

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v or []

    @property
    def is_dev(self) -> bool:
        return self.environment == "development"


settings = Settings()
