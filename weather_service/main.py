"""
Weather Service - Weather Forecast
"""
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from models import WeatherRequest, WeatherResponse
from services import WeatherService
from dependencies import get_redis, get_db
from utils import WEATHER_CONDITIONS, WEATHER_DESCRIPTIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Weather Service", description="Weather Forecast Service")


@app.get("/")
async def root():
    """Health check"""
    return {"message": "Weather Service is running", "timestamp": datetime.now().isoformat()}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with details"""
    from config import settings
    redis_client = get_redis()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "redis": "unknown",
            "database": "unknown",
            "openweather_api": "available" if settings.openweather_api_key else "unavailable"
        }
    }
    
    # Check Redis connection
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "available"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "available"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
    
    return health_status


@app.post("/weather/forecast", response_model=WeatherResponse)
async def get_weather_forecast(request: WeatherRequest):
    """Get  daysweather预测"""
    try:
        service = WeatherService(get_redis())
        return await service.get_weather_forecast(request)
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get weather forecast: {str(e)}")


@app.get("/weather/current")
async def get_current_weather(location: str):
    """Get 当前 daysweather"""
    try:
        service = WeatherService(get_redis())
        return await service.get_current_weather(location)
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current weather: {str(e)}")


@app.get("/weather/conditions")
async def get_weather_conditions():
    """Get 所有可用的 daysweather条件"""
    return {
        "conditions": WEATHER_CONDITIONS,
        "descriptions": WEATHER_DESCRIPTIONS
    }


@app.get("/weather/recommendations")
async def get_weather_recommendations(location: str, activity: str):
    """根据 daysweather和活动类型提供建议"""
    try:
        service = WeatherService(get_redis())
        return await service.get_weather_recommendations(location, activity)
    except Exception as e:
        logger.error(f"Error getting weather recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get weather recommendations: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
