"""Pydantic models describing core entities for the trip planner."""
from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, validator


ModeType = Literal["walk", "transit", "drive"]
PaceType = Literal["relaxed", "medium", "tight"]
ThemeType = Literal["food", "museum", "park", "viewpoint", "other"]


class DateRange(BaseModel):
    start: date
    end: date

    @validator("end")
    def validate_end(cls, value: date, values: dict[str, date]) -> date:
        start = values.get("start")
        if start and value < start:
            raise ValueError("End date must not be earlier than start date")
        return value


class TripConstraints(BaseModel):
    city: str
    dates: DateRange
    party_size: int = Field(default=2, ge=1)
    mode: ModeType = "walk"
    pace: PaceType = "medium"
    themes: List[str] = Field(default_factory=list)


class POISource(BaseModel):
    name: str
    url: str
    fetched_at: str


class CandidatePOI(BaseModel):
    poi_id: str
    name: str
    lat: float
    lon: float
    category: ThemeType | str
    popularity: float = Field(ge=0.0, le=1.0)
    min_dwell: int = Field(default=60, ge=15)
    source: POISource


class DistanceMatrix(BaseModel):
    mode: ModeType
    eta_min: List[tuple[str, str, float]]

    def lookup(self, origin: str, destination: str, default: float = 15.0) -> float:
        for o, d, eta in self.eta_min:
            if (o == origin and d == destination) or (o == destination and d == origin):
                return float(eta)
        return default


class WeatherByDate(BaseModel):
    date: date
    precip_prob: float
    note: str = ""


class WeatherSummary(BaseModel):
    by_date: List[WeatherByDate]

    def precipitation_for(self, day: date) -> Optional[WeatherByDate]:
        for entry in self.by_date:
            if entry.date == day:
                return entry
        return None


class RoutingParams(BaseModel):
    primary_mode: ModeType
    pace_coeff: float
    theme_weights: dict[str, float]
    buffer_ratio: float


class TransportInfo(BaseModel):
    mode: ModeType
    eta_min: float


class Slot(BaseModel):
    start: str
    end: str
    poi_id: Optional[str] = None
    type: Optional[str] = None
    transport: Optional[TransportInfo] = None


class DayPlan(BaseModel):
    date: date
    slots: List[Slot]
    day_total_time_min: float
    transit_share: float


class TripPlan(BaseModel):
    city: str
    days: List[DayPlan]
    sources: List[str]
    itinerary_text: str
    why_this_plan: str


__all__ = [
    "TripConstraints",
    "CandidatePOI",
    "DistanceMatrix",
    "WeatherSummary",
    "RoutingParams",
    "TripPlan",
    "Slot",
    "DayPlan",
]
