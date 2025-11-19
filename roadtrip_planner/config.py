"""
Configuration for the road trip planner.

Loads settings from environment variables or provides sensible defaults.
"""

import os
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration settings for the road trip planner."""

    # OpenAI API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str | None = os.getenv("OPENAI_BASE_URL")  # Optional custom endpoint

    # Model Names
    # Parser model: extracts structured RoadTripRequest from natural language
    PARSER_MODEL: str = os.getenv("PARSER_MODEL", "gpt-4")

    # Planner model: plans routes, selects POIs, etc.
    PLANNER_MODEL: str = os.getenv("PLANNER_MODEL", "gpt-4")

    # Renderer model: generates human-readable itinerary text
    RENDERER_MODEL: str = os.getenv("RENDERER_MODEL", "gpt-3.5-turbo")

    # LLM Settings
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000

    # Default Planning Parameters
    DEFAULT_MAX_DRIVE_HOURS: float = 5.0
    DEFAULT_NUM_DAYS: int = 3
    DEFAULT_BUDGET_LEVEL: Literal["low", "medium", "high"] = "medium"
    DEFAULT_LANGUAGE: Literal["en", "zh"] = "en"

    # Media Search Settings (for future API integrations)
    XIAOHONGSHU_API_KEY: str = os.getenv("XIAOHONGSHU_API_KEY", "")
    EXPEDIA_API_KEY: str = os.getenv("EXPEDIA_API_KEY", "")

    # Debug Settings
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    VERBOSE_TRACE: bool = os.getenv("VERBOSE_TRACE", "false").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not set. Please set it in .env file or environment variables."
            )


# Singleton config instance
config = Config()
