"""
Weather Service - Data Models
"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class WeatherRequest(BaseModel):
    """ daysweather请求模型"""
    location: str
    duration: int = 3  #  days数


class WeatherForecast(BaseModel):
    """Weather forecast model"""
    date: str
    temperature_min: float
    temperature_max: float
    condition: str
    humidity: int
    wind_speed: float
    description: str


class WeatherResponse(BaseModel):
    """ daysweather响应模型"""
    location: str
    forecast: List[WeatherForecast]
    current_weather: Optional[Dict] = None


class CurrentWeatherResponse(BaseModel):
    """当前 daysweather响应"""
    location: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    pressure: int
    visibility: float
    description: str


class WeatherRecommendationRequest(BaseModel):
    """ daysweather建议请求"""
    location: str
    activity: str  # outdoor, hiking, etc.

