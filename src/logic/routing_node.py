"""Routing node: derive routing parameters from constraints and weather."""
from __future__ import annotations

from typing import Any, Dict

from src.models import RoutingParams, TripConstraints, WeatherSummary

PACE_MAP = {"relaxed": 0.8, "medium": 1.0, "tight": 1.2}
BASE_BUFFER = 0.15
RAIN_BUFFER = 0.25


def routing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    constraints: TripConstraints = state["constraints"]
    weather: WeatherSummary = state.get("weather")

    pace_coeff = PACE_MAP.get(constraints.pace, 1.0)
    buffer_ratio = BASE_BUFFER
    if weather and weather.by_date:
        damp_days = [entry for entry in weather.by_date if entry.precip_prob > 0.5]
        if damp_days:
            buffer_ratio = RAIN_BUFFER

    theme_weights = {theme: 1.0 for theme in constraints.themes}
    for fallback in ["food", "museum", "park", "viewpoint", "other"]:
        theme_weights.setdefault(fallback, 0.7)

    params = RoutingParams(
        primary_mode=constraints.mode,
        pace_coeff=pace_coeff,
        theme_weights=theme_weights,
        buffer_ratio=buffer_ratio,
    )
    state["routing_params"] = params
    return state


__all__ = ["routing_node"]
