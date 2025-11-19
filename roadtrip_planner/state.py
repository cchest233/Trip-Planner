"""
State management for LangGraph workflow.

Defines RoadTripState and helper functions for state manipulation and debugging.
"""

from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field
from .models import (
    RoadTripRequest,
    MediaItem,
    RouteSkeleton,
    DailyPlan,
    Itinerary,
)


class RoadTripState(BaseModel):
    """
    State object for the road trip planning workflow.
    
    This state is passed between LangGraph nodes and accumulates
    information as the workflow progresses.
    """

    # Input
    user_query: str = Field(description="Original natural language query from user")

    # Parsed Request
    request: RoadTripRequest | None = Field(
        default=None,
        description="Structured request parsed from user_query"
    )

    # Media Search Results
    media_items: list[MediaItem] = Field(
        default_factory=list,
        description="Media items from content search"
    )

    # Route Planning
    route_skeleton: RouteSkeleton | None = Field(
        default=None,
        description="High-level route structure"
    )

    # POI Selection
    daily_plan: list[DailyPlan] = Field(
        default_factory=list,
        description="Detailed daily plans with selected POIs"
    )

    # Final Output
    itinerary: Itinerary | None = Field(
        default=None,
        description="Complete structured itinerary"
    )
    itinerary_text: str | None = Field(
        default=None,
        description="Human-readable itinerary text"
    )

    # Debug and Monitoring
    debug_trace: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Step-by-step execution trace for debugging"
    )

    class Config:
        arbitrary_types_allowed = True


def add_debug_event(
    state: RoadTripState,
    node_name: str,
    event_type: str,
    message: str,
    snapshot: dict[str, Any] | None = None
) -> RoadTripState:
    """
    Add a debug event to the state's debug trace.

    Args:
        state: Current RoadTripState
        node_name: Name of the node generating this event
        event_type: Type of event (e.g., 'start', 'complete', 'error', 'info')
        message: Human-readable message describing the event
        snapshot: Optional snapshot of relevant state data

    Returns:
        Updated state with new debug event
    """
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "node": node_name,
        "event_type": event_type,
        "message": message,
    }
    
    if snapshot:
        event["snapshot"] = snapshot

    state.debug_trace.append(event)
    return state


def log_node_start(state: RoadTripState, node_name: str) -> RoadTripState:
    """
    Log the start of a node execution.

    Args:
        state: Current RoadTripState
        node_name: Name of the node starting

    Returns:
        Updated state with start event
    """
    return add_debug_event(
        state,
        node_name=node_name,
        event_type="start",
        message=f"Starting {node_name} node"
    )


def log_node_complete(
    state: RoadTripState,
    node_name: str,
    details: str | None = None
) -> RoadTripState:
    """
    Log the completion of a node execution.

    Args:
        state: Current RoadTripState
        node_name: Name of the node completing
        details: Optional details about what was accomplished

    Returns:
        Updated state with completion event
    """
    message = f"Completed {node_name} node"
    if details:
        message += f": {details}"
    
    return add_debug_event(
        state,
        node_name=node_name,
        event_type="complete",
        message=message
    )


def log_node_error(
    state: RoadTripState,
    node_name: str,
    error: Exception
) -> RoadTripState:
    """
    Log an error during node execution.

    Args:
        state: Current RoadTripState
        node_name: Name of the node where error occurred
        error: The exception that was raised

    Returns:
        Updated state with error event
    """
    return add_debug_event(
        state,
        node_name=node_name,
        event_type="error",
        message=f"Error in {node_name}: {str(error)}",
        snapshot={"error_type": type(error).__name__}
    )


def get_state_summary(state: RoadTripState) -> dict[str, Any]:
    """
    Get a summary of the current state for debugging.

    Args:
        state: Current RoadTripState

    Returns:
        Dictionary with summary information
    """
    return {
        "has_request": state.request is not None,
        "media_items_count": len(state.media_items),
        "has_route_skeleton": state.route_skeleton is not None,
        "daily_plans_count": len(state.daily_plan),
        "has_itinerary": state.itinerary is not None,
        "has_itinerary_text": state.itinerary_text is not None,
        "debug_events_count": len(state.debug_trace),
    }
