"""
All tools for the road trip planner.

Includes media search, routing calculations, and other utility functions.
"""

from .models import MediaItem, RoadTripRequest
from typing import List, Dict, Any, Optional


# ============================================================================
# Media Search Tools
# ============================================================================

def media_search_stub(request: RoadTripRequest) -> list[MediaItem]:
    """
    Stub function for media search across multiple platforms.
    
    Currently returns mock data.
    """
    items = []
    
    origin = request.origin.lower()
    destination = (request.destination or request.origin).lower()
    
    # Generate mock items based on keywords
    if "san francisco" in origin or "san francisco" in destination:
        items.append(MediaItem(
            source="xiaohongshu",
            title="Golden Gate Bridge at Sunset - Must See!",
            url="https://xiaohongshu.com/mock/123",
            location_name="San Francisco, CA",
            score=0.95,
            tags=["city", "landmark", "photography"]
        ))
    
    if "los angeles" in origin or "los angeles" in destination:
        items.append(MediaItem(
            source="xiaohongshu",
            title="Best Beaches in LA - Local's Guide",
            url="https://xiaohongshu.com/mock/789",
            location_name="Los Angeles, CA",
            score=0.92,
            tags=["beach", "nature", "photography"]
        ))
    
    # Add generic coastal route items
    if any(keyword in origin + destination for keyword in ["california", "coast", "highway"]):
        items.append(MediaItem(
            source="xiaohongshu",
            title="Highway 1 Scenic Stops You Can't Miss",
            url="https://xiaohongshu.com/mock/202",
            location_name="Big Sur, CA",
            score=0.98,
            tags=["nature", "scenic", "coastal"]
        ))
    
    # If no items, add generic one
    if not items:
        items.append(MediaItem(
            source="xiaohongshu",
            title=f"Road Trip Guide: {request.origin} Area",
            url="https://xiaohongshu.com/mock/default1",
            location_name=request.origin,
            score=0.75,
            tags=["road trip", "guide"]
        ))
    
    # Sort by score
    items.sort(key=lambda x: x.score or 0, reverse=True)
    
    return items


# ============================================================================
# Routing Tools (Placeholders for Function Calling)
# ============================================================================

def calculate_route_distance(origin: str, destination: str) -> Dict[str, Any]:
    """
    Calculate distance and driving time between two locations.
    
    TODO: Implement with Google Distance Matrix API or Amap API
    """
    return {
        "distance_km": 100.0,
        "distance_miles": 62.1,
        "duration_hours": 1.5,
        "duration_minutes": 90,
        "status": "mock"
    }


def get_driving_directions(origin: str, destination: str, waypoints: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get turn-by-turn driving directions.
    
    TODO: Implement with Google Maps Directions API or Amap API
    """
    return {
        "route_summary": f"{origin} to {destination}",
        "total_distance_km": 100.0,
        "total_duration_hours": 1.5,
        "waypoints_count": len(waypoints) if waypoints else 0,
        "status": "mock"
    }


def search_nearby_places(location: str, place_type: str, radius_km: float = 10.0) -> List[Dict[str, Any]]:
    """
    Search for nearby places of interest.
    
    TODO: Implement with Google Places API or Amap POI API
    """
    return [{
        "name": f"Mock {place_type} near {location}",
        "address": location,
        "rating": 4.5,
        "status": "mock"
    }]


def geocode_location(address: str) -> Dict[str, Any]:
    """
    Convert address to coordinates.
    
    TODO: Implement with Google Geocoding API or Amap API
    """
    return {
        "address": address,
        "lat": 0.0,
        "lng": 0.0,
        "formatted_address": address,
        "status": "mock"
    }


# ============================================================================
# Tool Definitions for LLM Function Calling
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_route_distance",
            "description": "Calculate distance and driving time between two locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Starting location"},
                    "destination": {"type": "string", "description": "Ending location"}
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_driving_directions",
            "description": "Get detailed driving directions with waypoints",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "waypoints": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_nearby_places",
            "description": "Search for nearby places (restaurants, attractions, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "place_type": {"type": "string"},
                    "radius_km": {"type": "number"}
                },
                "required": ["location", "place_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "geocode_location",
            "description": "Convert address to latitude/longitude coordinates",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"}
                },
                "required": ["address"]
            }
        }
    }
]

# Mapping of function names to actual functions
TOOL_FUNCTIONS = {
    "calculate_route_distance": calculate_route_distance,
    "get_driving_directions": get_driving_directions,
    "search_nearby_places": search_nearby_places,
    "geocode_location": geocode_location,
}