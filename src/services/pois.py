"""POI service interface and demo implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, List

from src.config import get_settings
from src.models import CandidatePOI, POISource


class POIService(ABC):
    """Interface for fetching points of interest."""

    @abstractmethod
    def search(self, city: str, themes: Iterable[str], limit: int) -> List[CandidatePOI]:
        """Return a list of POI candidates for the given city."""


class DemoPOIService(POIService):
    """In-memory POI service for demos and tests."""

    def search(self, city: str, themes: Iterable[str], limit: int) -> List[CandidatePOI]:
        timestamp = datetime.utcnow().isoformat()
        base_source = POISource(name="DemoPOI", url="https://demo.local", fetched_at=timestamp)
        theme_list = list(themes)
        sample = [
            CandidatePOI(
                poi_id=f"{city.lower()}_{idx}",
                name=f"{city.title()} Highlight {idx}",
                lat=35.0 + idx * 0.01,
                lon=135.0 + idx * 0.01,
                category=theme_list[idx % len(theme_list)] if theme_list else "other",
                popularity=max(0.3, 1.0 - idx * 0.1),
                min_dwell=60 + idx * 15,
                source=base_source,
            )
            for idx in range(min(limit, 10))
        ]
        return sample


class ExternalPOIService(POIService):
    """Placeholder for real provider integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, city: str, themes: Iterable[str], limit: int) -> List[CandidatePOI]:
        raise NotImplementedError("Real POI provider integration pending.")


def get_poi_service() -> POIService:
    """Factory returning the active POI service."""

    settings = get_settings()
    if settings.api_key_poi:
        return ExternalPOIService(api_key=settings.api_key_poi)
    return DemoPOIService()


__all__ = ["POIService", "DemoPOIService", "get_poi_service"]
