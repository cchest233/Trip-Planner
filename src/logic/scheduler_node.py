"""Scheduler node: assemble day plans from POIs."""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Tuple

from src.models import (
    CandidatePOI,
    DayPlan,
    DistanceMatrix,
    RoutingParams,
    Slot,
    TransportInfo,
    TripConstraints,
    TripPlan,
)
from src.utils.geo import cluster_pois, select_top_pois
from src.utils.timebox import allocate_day_blocks


MIN_ACTIVITIES = 3
MAX_ACTIVITIES = 4


def compute_poi_scores(pois: List[CandidatePOI], theme_weights: Dict[str, float]) -> Dict[str, float]:
    """Score POIs using popularity weighted by theme preference."""

    scores: Dict[str, float] = {}
    for poi in pois:
        weight = theme_weights.get(str(poi.category), theme_weights.get("other", 0.7))
        scores[poi.poi_id] = poi.popularity * weight
    return scores


def _choose_cluster_order(clusters: Dict[int, List[CandidatePOI]], scores: Dict[str, float]) -> List[int]:
    ranked = sorted(
        clusters.items(),
        key=lambda item: sum(scores.get(poi.poi_id, 0.0) for poi in item[1]),
        reverse=True,
    )
    return [cluster_id for cluster_id, _ in ranked]


def _build_day_slots(
    pois: List[CandidatePOI],
    matrix: DistanceMatrix,
    routing_params: RoutingParams,
) -> Tuple[List[Slot], float, float]:
    activities: List[Tuple[str, float, float]] = []
    prev_poi: CandidatePOI | None = None
    buffer_ratio = routing_params.buffer_ratio
    for poi in pois:
        travel = 0.0
        if prev_poi is not None:
            eta = matrix.lookup(prev_poi.poi_id, poi.poi_id)
            travel = eta * (1.0 + buffer_ratio)
        dwell = poi.min_dwell * routing_params.pace_coeff
        activities.append((poi.poi_id, dwell, travel))
        prev_poi = poi
    slots_raw, day_total, transit_share = allocate_day_blocks(activities)
    slots: List[Slot] = []
    for entry in slots_raw:
        if "transport" in entry:
            slots.append(
                Slot(
                    start=entry["start"],
                    end=entry["end"],
                    type="transit",
                    transport=TransportInfo(
                        mode=routing_params.primary_mode,
                        eta_min=entry["transport"]["eta_min"],
                    ),
                )
            )
        elif entry.get("type") == "meal":
            slots.append(Slot(start=entry["start"], end=entry["end"], type="meal"))
        else:
            slots.append(Slot(start=entry["start"], end=entry["end"], poi_id=entry["poi_id"]))
    return slots, day_total, transit_share


def scheduler_node(state: Dict[str, Any]) -> Dict[str, Any]:
    constraints: TripConstraints = state["constraints"]
    pois: List[CandidatePOI] = state.get("pois", [])
    routing_params: RoutingParams = state["routing_params"]
    matrix: DistanceMatrix = state.get("matrix")

    scores = compute_poi_scores(pois, routing_params.theme_weights)
    clusters = cluster_pois(pois)
    ordered_clusters = _choose_cluster_order(clusters, scores)

    num_days = (constraints.dates.end - constraints.dates.start).days + 1
    day_plans: List[DayPlan] = []
    cluster_index = 0

    for day_offset in range(num_days):
        if not ordered_clusters:
            break
        cluster_id = ordered_clusters[cluster_index % len(ordered_clusters)]
        cluster_index += 1
        cluster_pois_list = select_top_pois(
            clusters[cluster_id], scores, limit=MAX_ACTIVITIES
        )
        if len(cluster_pois_list) < MIN_ACTIVITIES and len(pois) >= MIN_ACTIVITIES:
            additional = [poi for poi in pois if poi not in cluster_pois_list]
            cluster_pois_list.extend(additional[: MIN_ACTIVITIES - len(cluster_pois_list)])
        cluster_pois_list = cluster_pois_list[:MAX_ACTIVITIES]

        slots, day_total, transit_share = _build_day_slots(
            cluster_pois_list, matrix, routing_params
        )
        day_plans.append(
            DayPlan(
                date=constraints.dates.start + timedelta(days=day_offset),
                slots=slots,
                day_total_time_min=day_total,
                transit_share=transit_share,
            )
        )

    sources = ["POIService", "RoutingService", "WeatherService"]
    trip_plan = TripPlan(
        city=constraints.city,
        days=day_plans,
        sources=sources,
        itinerary_text="",
        why_this_plan="",
    )
    state["trip_plan"] = trip_plan
    return state


__all__ = ["scheduler_node", "compute_poi_scores"]
