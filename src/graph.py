"""LangGraph wiring for the trip planner workflow."""
from __future__ import annotations

from typing import List, TypedDict

from langgraph.graph import END, StateGraph

from src.logic.fetcher_node import fetcher_node
from src.logic.narrator_node import narrator_node
from src.logic.router_node import router_node
from src.logic.routing_node import routing_node
from src.logic.scheduler_node import scheduler_node
from src.models import CandidatePOI, DistanceMatrix, RoutingParams, TripConstraints, TripPlan, WeatherSummary


class TripState(TypedDict, total=False):
    constraints: TripConstraints
    pois: List[CandidatePOI]
    matrix: DistanceMatrix
    weather: WeatherSummary
    routing_params: RoutingParams
    trip_plan: TripPlan


def build_graph() -> StateGraph:
    graph = StateGraph(TripState)
    graph.add_node("router_node", router_node)
    graph.add_node("fetcher_node", fetcher_node)
    graph.add_node("routing_node", routing_node)
    graph.add_node("scheduler_node", scheduler_node)
    graph.add_node("narrator_node", narrator_node)

    graph.set_entry_point("router_node")
    graph.add_edge("router_node", "fetcher_node")
    graph.add_edge("fetcher_node", "routing_node")
    graph.add_edge("routing_node", "scheduler_node")
    graph.add_edge("scheduler_node", "narrator_node")
    graph.add_edge("narrator_node", END)
    return graph


__all__ = ["TripState", "build_graph"]
