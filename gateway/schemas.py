"""请求和响应模型定义"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class TripRequest(BaseModel):
    """Trip plan request"""
    origin: str
    destination: str
    preferences: List[str]
    duration: int
    user_id: Optional[int] = 1


class TripResponse(BaseModel):
    """Trip plan response"""
    trip_id: int
    status: str
    route: Optional[Dict] = None
    weather: Optional[List[Dict]] = None
    pois: Optional[List[Dict]] = None
    ai_summary: Optional[Dict] = None

