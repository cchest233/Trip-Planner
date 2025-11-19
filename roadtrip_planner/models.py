"""
Pydantic models for the road trip planner.

Defines structured data models for requests, media items, routes, POIs, and itineraries.
"""

from typing import Literal
from pydantic import BaseModel, Field


class Preferences(BaseModel):
    """User preferences for trip planning."""

    nature: float = Field(default=0.5, ge=0.0, le=1.0, description="Interest in nature/outdoor activities")
    city: float = Field(default=0.5, ge=0.0, le=1.0, description="Interest in city/urban attractions")
    food: float = Field(default=0.5, ge=0.0, le=1.0, description="Interest in food/culinary experiences")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nature": 0.8,
                "city": 0.3,
                "food": 0.9
            }
        }


class RoadTripRequest(BaseModel):
    """Structured representation of a road trip request."""

    origin: str = Field(description="Starting location (city, address, or landmark)")
    destination: str | None = Field(default=None, description="Ending location (can be same as origin for loop trips)")
    start_date: str | None = Field(default=None, description="Trip start date (ISO format or natural language)")
    num_days: int | None = Field(default=None, ge=1, le=30, description="Number of days for the trip")
    max_drive_hours_per_day: float | None = Field(
        default=None,
        ge=1.0,
        le=12.0,
        description="Maximum driving hours per day"
    )
    preferences: Preferences = Field(default_factory=Preferences, description="User preferences")
    budget_level: Literal["low", "medium", "high"] | None = Field(
        default=None,
        description="Budget level for accommodations and activities"
    )
    language: Literal["en", "zh"] | None = Field(
        default=None,
        description="Output language preference"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "San Francisco, CA",
                "destination": "Los Angeles, CA",
                "start_date": "2024-06-15",
                "num_days": 3,
                "max_drive_hours_per_day": 5.0,
                "preferences": {
                    "nature": 0.7,
                    "city": 0.5,
                    "food": 0.9
                },
                "budget_level": "medium",
                "language": "en"
            }
        }


class MediaItem(BaseModel):
    """Media item from content search (Xiaohongshu, Expedia, etc.)."""

    source: str = Field(description="Source platform (e.g., 'xiaohongshu', 'expedia', 'trips')")
    title: str = Field(description="Title or description of the item")
    url: str | None = Field(default=None, description="URL to the content")
    location_name: str | None = Field(default=None, description="Associated location name")
    score: float | None = Field(default=None, ge=0.0, le=1.0, description="Relevance score")
    tags: list[str] | None = Field(default=None, description="Tags or categories")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "xiaohongshu",
                "title": "Best coastal views on Highway 1",
                "url": "https://example.com/post/123",
                "location_name": "Big Sur, CA",
                "score": 0.95,
                "tags": ["coastal", "scenic", "nature"]
            }
        }


class RouteDaySkeleton(BaseModel):
    """High-level route plan for a single day."""

    day_index: int = Field(ge=1, description="Day number (1-indexed)")
    start_location: str = Field(description="Starting location for this day")
    end_location: str = Field(description="Ending location for this day")
    candidate_stops: list[str] = Field(
        default_factory=list,
        description="Candidate stop locations along the route"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "day_index": 1,
                "start_location": "San Francisco, CA",
                "end_location": "Monterey, CA",
                "candidate_stops": ["Half Moon Bay", "Santa Cruz", "Carmel-by-the-Sea"]
            }
        }


class RouteSkeleton(BaseModel):
    """High-level route structure for the entire trip."""

    days: list[RouteDaySkeleton] = Field(description="Daily route segments")

    class Config:
        json_schema_extra = {
            "example": {
                "days": [
                    {
                        "day_index": 1,
                        "start_location": "San Francisco, CA",
                        "end_location": "Monterey, CA",
                        "candidate_stops": ["Half Moon Bay", "Santa Cruz"]
                    }
                ]
            }
        }


class POI(BaseModel):
    """Point of Interest for a specific stop."""

    name: str = Field(description="Name of the POI")
    location_name: str = Field(description="Location/city name")
    category: Literal["nature", "city", "food", "other"] = Field(description="Category of POI")
    score: float | None = Field(default=None, ge=0.0, le=1.0, description="Relevance/quality score")
    source: str | None = Field(default=None, description="Data source (e.g., 'xiaohongshu', 'manual')")
    description: str | None = Field(default=None, description="Brief description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bixby Creek Bridge",
                "location_name": "Big Sur, CA",
                "category": "nature",
                "score": 0.98,
                "source": "xiaohongshu",
                "description": "Iconic bridge with stunning coastal views"
            }
        }


class DailyPlan(BaseModel):
    """Detailed plan for a single day of the trip."""

    day_index: int = Field(ge=1, description="Day number (1-indexed)")
    start_location: str = Field(description="Starting location")
    end_location: str = Field(description="Ending location")
    stops: list[POI] = Field(default_factory=list, description="POIs to visit this day")
    estimated_drive_hours: float | None = Field(
        default=None,
        ge=0.0,
        description="Estimated total driving time"
    )
    notes: str | None = Field(default=None, description="Additional notes or recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "day_index": 1,
                "start_location": "San Francisco, CA",
                "end_location": "Monterey, CA",
                "stops": [
                    {
                        "name": "Half Moon Bay State Beach",
                        "location_name": "Half Moon Bay, CA",
                        "category": "nature",
                        "score": 0.85
                    }
                ],
                "estimated_drive_hours": 3.5,
                "notes": "Scenic coastal drive"
            }
        }


class Itinerary(BaseModel):
    """Complete trip itinerary with all daily plans."""

    days: list[DailyPlan] = Field(description="Daily plans for the entire trip")
    summary: str | None = Field(default=None, description="Overall trip summary")
    total_drive_hours: float | None = Field(
        default=None,
        ge=0.0,
        description="Total estimated driving time"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "days": [
                    {
                        "day_index": 1,
                        "start_location": "San Francisco",
                        "end_location": "Monterey",
                        "stops": []
                    }
                ],
                "summary": "A 3-day coastal road trip from SF to LA",
                "total_drive_hours": 12.5
            }
        }
