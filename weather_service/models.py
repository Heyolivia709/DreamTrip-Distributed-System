"""
Weather Service - Data Models
"""
from typing import Dict, List, Optional
from pydantic import BaseModel


class WeatherRequest(BaseModel):
    """Weather request model"""
    location: str
    duration: int = 3  # Number of days


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
    """Weather response model"""
    location: str
    forecast: List[WeatherForecast]
    current_weather: Optional[Dict] = None


class CurrentWeatherResponse(BaseModel):
    """Current weather response"""
    location: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    pressure: int
    visibility: float
    description: str


class WeatherRecommendationRequest(BaseModel):
    """Weather recommendation request"""
    location: str
    activity: str  # outdoor, hiking, etc.

