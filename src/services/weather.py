"""Weather service interface and demo implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Iterable

from src.config import get_settings
from src.models import WeatherByDate, WeatherSummary


class WeatherService(ABC):
    """Interface returning weather summaries."""

    @abstractmethod
    def summary(self, city: str, dates: Iterable[date]) -> WeatherSummary:
        """Return weather summary for provided dates."""


class DemoWeatherService(WeatherService):
    """Demo weather service returning mild conditions."""

    def summary(self, city: str, dates: Iterable[date]) -> WeatherSummary:
        results = []
        base_prob = 0.2
        for idx, day in enumerate(sorted(dates)):
            results.append(
                WeatherByDate(
                    date=day,
                    precip_prob=min(0.8, base_prob + 0.05 * idx),
                    note="Expect comfortable temperatures.",
                )
            )
        return WeatherSummary(by_date=results)


class ExternalWeatherService(WeatherService):
    """Placeholder for real weather integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def summary(self, city: str, dates: Iterable[date]) -> WeatherSummary:
        raise NotImplementedError("Real weather provider integration pending.")


def get_weather_service() -> WeatherService:
    settings = get_settings()
    if settings.api_key_weather:
        return ExternalWeatherService(api_key=settings.api_key_weather)
    return DemoWeatherService()


__all__ = ["WeatherService", "DemoWeatherService", "get_weather_service"]
