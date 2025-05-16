"""Request and response model definitions"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class TripRequest(BaseModel):
    origin: str
    destination: str
    preferences: List[str]
    duration: int
    user_id: Optional[int] = 1


class TripResponse(BaseModel):
    trip_id: int
    status: str
    route: Optional[Dict] = None
    weather: Optional[List[Dict]] = None
    pois: Optional[List[Dict]] = None
    ai_summary: Optional[Dict] = None
