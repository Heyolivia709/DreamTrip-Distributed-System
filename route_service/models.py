"""
Route Service - Data Models
"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class RouteRequest(BaseModel):
    """路线请求模型"""
    origin: str
    destination: str
    mode: str = "driving"  # driving, walking, transit
    avoid: Optional[List[str]] = None  # tolls, highways, ferries


class RouteResponse(BaseModel):
    """路线响应模型"""
    origin: str
    destination: str
    distance: str
    duration: str
    steps: List[str]
    polyline: Optional[str] = None
    bounds: Optional[Dict] = None


class GeocodingRequest(BaseModel):
    """地理编码请求"""
    address: str


class GeocodingResponse(BaseModel):
    """地理编码响应"""
    address: str
    latitude: float
    longitude: float
    formatted_address: str


class ReverseGeocodingResponse(BaseModel):
    """反向地理编码响应"""
    latitude: float
    longitude: float
    address: str
    components: List[Dict]


class NearbyPlacesRequest(BaseModel):
    """附近地点请求"""
    lat: float
    lng: float
    radius: int = 5000
    place_type: str = "tourist_attraction"


class Place(BaseModel):
    """地点模型"""
    name: str
    place_id: Optional[str] = None
    rating: Optional[float] = None
    vicinity: Optional[str] = None
    types: Optional[List[str]] = None
    geometry: Optional[Dict] = None


class NearbyPlacesResponse(BaseModel):
    """附近地点响应"""
    places: List[Place]

