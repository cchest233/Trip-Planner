"""Application configuration and environment handling."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    llm_provider: str = Field(
        default="demo",
        alias="LLM_PROVIDER",
        description="Identifier for the LLM provider to use via LangChain.",
    )
    llm_model: Optional[str] = Field(
        default=None,
        alias="LLM_MODEL",
        description="Optional model identifier for real LLM providers.",
    )

    api_key_poi: Optional[str] = Field(default=None, alias="API_KEY_POI")
    api_key_routing: Optional[str] = Field(default=None, alias="API_KEY_ROUTING")
    api_key_weather: Optional[str] = Field(default=None, alias="API_KEY_WEATHER")

    cache_backend: str = Field(
        default="memory",
        alias="CACHE_BACKEND",
        description="Cache backend selector. Defaults to in-memory store.",
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
        description="Redis connection URL if CACHE_BACKEND=redis.",
    )

    default_top_n_pois: int = Field(
        default=30,
        alias="DEFAULT_TOP_N_POIS",
        description="Default number of POIs to request from providers.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


__all__ = ["Settings", "get_settings"]
