"""Application configuration — reads from environment / .env file."""
from __future__ import annotations

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    mistral_api_key: str = ""
    together_api_key: str = ""
    database_url: str = "sqlite:///./news.db"
    tz: str = "Europe/Bucharest"
    daily_run_hour: int = 8
    admin_api_key: str = ""

    # Path to the sources YAML catalog
    sources_yaml: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "sources",
        "top_100_ai_sources.yaml",
    )

    # Path to the user custom sources YAML
    custom_sources_yaml: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "sources",
        "custom_sources.yaml",
    )


settings = Settings()
