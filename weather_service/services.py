"""
Weather Service - Business Logic Layer
"""
import json
import logging
from datetime import datetime, timedelta

import httpx
import redis

from models import WeatherRequest, WeatherResponse, WeatherForecast
from utils import generate_weather_recommendations
from config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """Weather Service Class"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.api_key = settings.openweather_api_key
    
    async def get_weather_forecast(self, request: WeatherRequest) -> WeatherResponse:
        """Get weather forecast"""
        
        # Check cache
        cache_key = f"weather:{request.location}:{request.duration}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Weather cache hit for {cache_key}")
            return WeatherResponse(**json.loads(cached_result))
        
        # Get weather data
        if not self.api_key:
            raise Exception("OpenWeather API key not configured")
        
        try:
            result = await self._get_weather_from_api(request)
        except Exception as e:
            logger.error(f"OpenWeather API error: {e}")
            raise Exception(f"Failed to get weather data: {e}")
        
        # Cache result (30 minutes)
        self.redis.setex(cache_key, 1800, json.dumps(result.model_dump()))
        
        logger.info(f"Weather forecast generated for {request.location}")
        return result
    
    async def _get_weather_from_api(self, request: WeatherRequest) -> WeatherResponse:
        """Get weather data from OpenWeather API"""
        
        # Get current  daysweather
        current_url = "http://api.openweathermap.org/data/2.5/weather"
        current_params = {
            "q": request.location,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        async with httpx.AsyncClient() as client:
            current_response = await client.get(current_url, params=current_params)
            current_response.raise_for_status()
            current_data = current_response.json()
        
        # Get weather forecast
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        forecast_params = {
            "q": request.location,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        async with httpx.AsyncClient() as client:
            forecast_response = await client.get(forecast_url, params=forecast_params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
        
        # Process current weather
        current_weather = {
            "temperature": current_data["main"]["temp"],
            "condition": current_data["weather"][0]["description"],
            "humidity": current_data["main"]["humidity"],
            "wind_speed": current_data["wind"]["speed"],
            "description": current_data["weather"][0]["description"]
        }
        
        # Process weather forecast
        forecast = []
        today = datetime.now().date()
        
        # Group forecast data by date
        daily_forecasts = {}
        for item in forecast_data["list"]:
            date = datetime.fromtimestamp(item["dt"]).date()
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(item)
        
        # Generate daily forecast
        for i in range(request.duration):
            target_date = today + timedelta(days=i)
            if target_date in daily_forecasts:
                day_data = daily_forecasts[target_date]
                
                # Calculate daily min/max temperature
                temps = [item["main"]["temp"] for item in day_data]
                temp_min = min(temps)
                temp_max = max(temps)
                
                # Get main weather condition
                conditions = [item["weather"][0]["description"] for item in day_data]
                main_condition = max(set(conditions), key=conditions.count)
                
                # Calculate average humidity and wind speed
                humidity = sum(item["main"]["humidity"] for item in day_data) / len(day_data)
                wind_speed = sum(item["wind"]["speed"] for item in day_data) / len(day_data)
                
                forecast.append(WeatherForecast(
                    date=target_date.isoformat(),
                    temperature_min=round(temp_min, 1),
                    temperature_max=round(temp_max, 1),
                    condition=main_condition,
                    humidity=int(humidity),
                    wind_speed=round(wind_speed, 1),
                    description=main_condition
                ))
        
        return WeatherResponse(
            location=request.location,
            forecast=forecast,
            current_weather=current_weather
        )
    
    async def get_current_weather(self, location: str) -> dict:
        """Get current weather"""
        
        cache_key = f"current_weather:{location}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Current weather cache hit for {cache_key}")
            return json.loads(cached_result)
        
        if not self.api_key:
            raise Exception("OpenWeather API key not configured")
        
        # Get current weather from API
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "lang": "en"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            result = {
                "location": location,
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", 0) / 1000,  # Convert to kilometers
                "description": data["weather"][0]["description"]
            }
        except Exception as e:
            logger.error(f"OpenWeather API error: {e}")
            raise Exception(f"Failed to get current weather: {e}")
        
        # Cache result (10 minutes)
        self.redis.setex(cache_key, 600, json.dumps(result))
        
        return result
    
    async def get_weather_recommendations(self, location: str, activity: str) -> dict:
        """Provide recommendations based on weather and activity type"""
        
        # Get current  daysweather
        current_weather = await self.get_current_weather(location)
        condition = current_weather["condition"]
        temperature = current_weather["temperature"]
        
        # Provide recommendations based on weather conditions and activity type
        recommendations = generate_weather_recommendations(condition, temperature, activity)
        
        return {
            "location": location,
            "activity": activity,
            "current_weather": current_weather,
            "recommendations": recommendations
        }

