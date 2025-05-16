"""Weather database operations"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session

from models import WeatherForecast
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class WeatherRepository(BaseRepository):
    """Weather database operations"""
    
    @staticmethod
    def save_weather_forecasts(
        db: Session, 
        trip_id: int, 
        location: str, 
        forecasts: List[Dict]
    ) -> bool:
        """Save weather forecast information"""
        def _save():
            for day_weather in forecasts:
                weather = WeatherForecast(
                    trip_plan_id=trip_id,
                    location=location,
                    date=day_weather["date"],
                    temperature_min=day_weather.get("temp_min"),
                    temperature_max=day_weather.get("temp_max"),
                    condition=day_weather.get("condition"),
                    humidity=day_weather.get("humidity"),
                    wind_speed=day_weather.get("wind_speed")
                )
                db.add(weather)
            return True
        
        result = BaseRepository._execute_with_rollback(db, _save)
        if result:
            BaseRepository._log_success("Weather info saved", trip_id)
        return result is not None
