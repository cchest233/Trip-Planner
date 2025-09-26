"""Simple timeboxing helpers for day planning."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List, Tuple


DAY_START = datetime.strptime("09:00", "%H:%M")
LUNCH_TIME = datetime.strptime("12:30", "%H:%M")
LUNCH_DURATION = timedelta(minutes=60)


def format_time(value: datetime) -> str:
    return value.strftime("%H:%M")


def allocate_day_blocks(
    activities: Iterable[Tuple[str, float, float]],
) -> Tuple[List[dict], float, float]:
    """Allocate activities into day timeline.

    Each activity tuple is (poi_id, dwell_minutes, travel_minutes_before).
    """

    current = DAY_START
    slots: List[dict] = []
    transit_total = 0.0

    for poi_id, dwell, travel in activities:
        if travel:
            transit_total += travel
            slots.append(
                {
                    "start": format_time(current),
                    "end": format_time(current + timedelta(minutes=travel)),
                    "transport": {
                        "eta_min": travel,
                    },
                }
            )
            current += timedelta(minutes=travel)

        if current <= LUNCH_TIME < current + timedelta(minutes=dwell):
            slots.append(
                {
                    "start": format_time(LUNCH_TIME),
                    "end": format_time(LUNCH_TIME + LUNCH_DURATION),
                    "type": "meal",
                }
            )
            current = LUNCH_TIME + LUNCH_DURATION

        slots.append(
            {
                "start": format_time(current),
                "end": format_time(current + timedelta(minutes=dwell)),
                "poi_id": poi_id,
            }
        )
        current += timedelta(minutes=dwell)

    day_total = (current - DAY_START).total_seconds() / 60.0
    transit_share = transit_total / day_total if day_total else 0.0
    return slots, day_total, transit_share


__all__ = ["allocate_day_blocks", "DAY_START", "LUNCH_TIME"]
