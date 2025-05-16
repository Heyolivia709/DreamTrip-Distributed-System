"""
POI Service - Data Models
"""
from typing import List, Optional
from pydantic import BaseModel


class POIRequest(BaseModel):
    """POI请求模型"""
    location: str
    preferences: List[str] = ["tourist_attraction"]
    radius: int = 5000  # 搜索半径（米）


class POI(BaseModel):
    """POI模型"""
    name: str
    category: str
    rating: float
    address: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    opening_hours: Optional[str] = None
    price_level: Optional[int] = None


class POIResponse(BaseModel):
    """POI响应模型"""
    location: str
    pois: List[POI]
    total_count: int


class PlaceDetailsRequest(BaseModel):
    """地点详情请求"""
    place_id: str


class PlaceDetailsResponse(BaseModel):
    """地点详情响应"""
    name: str
    rating: float
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[List[str]] = None
    reviews: Optional[List[dict]] = None

