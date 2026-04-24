"""
SoukAI Configuration
Manages environment variables and application settings via pydantic-settings.
"""

from __future__ import annotations

import json
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./soukai.db"

    # App metadata
    API_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "SoukAI"
    PROJECT_DESCRIPTION: str = (
        "AI Winning Product Analyzer for Moroccan COD E-commerce"
    )

    # CORS – list of allowed origins.
    # For local development the common Vite and CRA dev server ports are included.
    # Override in production .env:  CORS_ORIGINS=["https://yourdomain.com"]
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            # Fallback: comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


settings = Settings()
