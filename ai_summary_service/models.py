"""
AI Summary Service - Data Models
"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class AISummaryRequest(BaseModel):
    """AI summary request model"""
    origin: str
    destination: str
    preferences: List[str]
    duration: int
    route: Optional[Dict] = None
    weather: Optional[List[Dict]] = None
    pois: Optional[List[Dict]] = None


class DayItinerary(BaseModel):
    """Daily itinerary model"""
    day: int
    title: str
    activities: List[str]


class AISummaryResponse(BaseModel):
    """AI summary response model"""
    summary: str
    recommendations: str
    tips: str
    itinerary: Optional[List[DayItinerary]] = None


class CustomizationRequest(BaseModel):
    """Custom itinerary request"""
    trip_request: AISummaryRequest
    custom_requirements: str

