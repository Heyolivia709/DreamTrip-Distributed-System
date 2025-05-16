"""
Route Service - Data Models
"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class RouteRequest(BaseModel):
    """Route request model"""
    origin: str
    destination: str
    mode: str = "driving"  # driving, walking, transit
    avoid: Optional[List[str]] = None  # tolls, highways, ferries


class RouteResponse(BaseModel):
    """Route response model"""
    origin: str
    destination: str
    distance: str
    duration: str
    steps: List[str]
    polyline: Optional[str] = None
    bounds: Optional[Dict] = None


class GeocodingRequest(BaseModel):
    """Geocoding request"""
    address: str


class GeocodingResponse(BaseModel):
    """Geocoding response"""
    address: str
    latitude: float
    longitude: float
    formatted_address: str


class ReverseGeocodingResponse(BaseModel):
    """Reverse geocoding response"""
    latitude: float
    longitude: float
    address: str
    components: List[Dict]


class NearbyPlacesRequest(BaseModel):
    """Nearby places request"""
    lat: float
    lng: float
    radius: int = 5000
    place_type: str = "tourist_attraction"


class Place(BaseModel):
    """Place model"""
    name: str
    place_id: Optional[str] = None
    rating: Optional[float] = None
    vicinity: Optional[str] = None
    types: Optional[List[str]] = None
    geometry: Optional[Dict] = None


class NearbyPlacesResponse(BaseModel):
    """Nearby places response"""
    places: List[Place]

