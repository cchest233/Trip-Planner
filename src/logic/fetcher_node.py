"""Fetcher node: gather data from services."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from src.config import get_settings
from src.models import TripConstraints
from src.services.pois import get_poi_service
from src.services.routing import get_routing_service
from src.services.weather import get_weather_service


def _date_range(constraints: TripConstraints) -> List[date]:
    days: List[date] = []
    current = constraints.dates.start
    while current <= constraints.dates.end:
        days.append(current)
        current += timedelta(days=1)
    return days


def fetcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    constraints: TripConstraints = state["constraints"]
    settings = get_settings()

    poi_service = get_poi_service()
    routing_service = get_routing_service()
    weather_service = get_weather_service()

    pois = poi_service.search(
        city=constraints.city,
        themes=constraints.themes,
        limit=settings.default_top_n_pois,
    )
    matrix = routing_service.matrix(mode=constraints.mode, pois=pois)
    weather = weather_service.summary(city=constraints.city, dates=_date_range(constraints))

    state.update({
        "pois": pois,
        "matrix": matrix,
        "weather": weather,
    })
    return state


__all__ = ["fetcher_node"]
