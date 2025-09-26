"""Router node: ensure constraints exist within state."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

from src.models import DateRange, TripConstraints


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Populate TripConstraints in state, applying defaults."""

    constraints = state.get("constraints")
    if isinstance(constraints, TripConstraints):
        return state

    raw = constraints or state.get("raw_constraints", {})
    city = raw.get("city") or state.get("city") or "Unknown"
    start = raw.get("start") or state.get("start")
    end = raw.get("end") or state.get("end") or start
    if not start:
        start = date.today().isoformat()
    if not end:
        end = start
    dates = DateRange(start=date.fromisoformat(start), end=date.fromisoformat(end))
    trip_constraints = TripConstraints(
        city=city,
        dates=dates,
        party_size=int(raw.get("party_size", state.get("party", 2))),
        mode=raw.get("mode", state.get("mode", "walk")),
        pace=raw.get("pace", state.get("pace", "medium")),
        themes=raw.get("themes", state.get("themes", [])),
    )
    state["constraints"] = trip_constraints
    return state


__all__ = ["router_node"]
