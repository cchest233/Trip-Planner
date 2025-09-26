"""Routing service interface and demo implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from src.config import get_settings
from src.models import CandidatePOI, DistanceMatrix, ModeType


class RoutingService(ABC):
    """Interface providing travel estimates between POIs."""

    @abstractmethod
    def matrix(self, mode: ModeType, pois: Iterable[CandidatePOI]) -> DistanceMatrix:
        """Return a sparse distance matrix for the given POIs."""


class DemoRoutingService(RoutingService):
    """Demo routing service returning synthetic travel times."""

    def matrix(self, mode: ModeType, pois: Iterable[CandidatePOI]) -> DistanceMatrix:
        poi_list = list(pois)
        triples: List[tuple[str, str, float]] = []
        for idx, origin in enumerate(poi_list):
            for jdx, dest in enumerate(poi_list):
                if idx >= jdx:
                    continue
                eta = 12.0 + abs(idx - jdx) * 6.0
                if mode == "drive":
                    eta *= 0.6
                elif mode == "transit":
                    eta *= 0.9
                triples.append((origin.poi_id, dest.poi_id, eta))
        return DistanceMatrix(mode=mode, eta_min=triples)


class ExternalRoutingService(RoutingService):
    """Placeholder for real routing provider integration."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def matrix(self, mode: ModeType, pois: Iterable[CandidatePOI]) -> DistanceMatrix:
        raise NotImplementedError("Real routing provider integration pending.")


def get_routing_service() -> RoutingService:
    settings = get_settings()
    if settings.api_key_routing:
        return ExternalRoutingService(api_key=settings.api_key_routing)
    return DemoRoutingService()


__all__ = ["RoutingService", "DemoRoutingService", "get_routing_service"]
