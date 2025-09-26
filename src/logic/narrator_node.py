"""Narrator node: generate textual summary for the trip plan."""
from __future__ import annotations

from typing import Any, Dict

from src.llm.client import UnsupportedProviderError, get_llm
from src.models import TripPlan


PROMPT_TEMPLATE = (
    "Create a friendly and concise summary for a {days}-day trip to {city}. "
    "Highlight daily focus and overall vibe in 3-4 sentences."
)


def narrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    trip_plan: TripPlan = state["trip_plan"]

    try:
        llm = get_llm()
        prompt = PROMPT_TEMPLATE.format(days=len(trip_plan.days), city=trip_plan.city)
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            text = response.content  # type: ignore[attr-defined]
        else:
            text = str(response)
    except UnsupportedProviderError as exc:
        text = f"Narration unavailable: {exc}"

    trip_plan.itinerary_text = text
    trip_plan.why_this_plan = "Balanced mix of top highlights with manageable pacing."
    state["trip_plan"] = trip_plan
    return state


__all__ = ["narrator_node"]
