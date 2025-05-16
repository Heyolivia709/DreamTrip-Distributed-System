"""
POI Service - Point of Interest Recommendations
"""
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from models import POIRequest, POIResponse, PlaceDetailsResponse
from services import POIService
from dependencies import get_gmaps, get_redis, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="POI Service", description="Point of Interest Recommendation Service")


@app.get("/")
async def root():
    """Health check"""
    return {"message": "POI Service is running", "timestamp": datetime.now().isoformat()}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with details"""
    gmaps = get_gmaps()
    redis_client = get_redis()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "google_places": "available" if gmaps else "unavailable",
            "redis": "unknown",
            "database": "unknown"
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


@app.post("/poi/recommendations", response_model=POIResponse)
async def get_poi_recommendations(request: POIRequest):
    """Get POI推荐"""
    try:
        service = POIService(get_gmaps(), get_redis())
        return await service.get_poi_recommendations(request)
    except Exception as e:
        logger.error(f"Error getting POI recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get POI recommendations: {str(e)}")


@app.get("/poi/details/{place_id}")
async def get_place_details(place_id: str):
    """Get 地点详情"""
    try:
        service = POIService(get_gmaps(), get_redis())
        return await service.get_place_details(place_id)
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get place details: {str(e)}")


@app.get("/poi/categories")
async def get_poi_categories():
    """Get 所有可用的POI类别"""
    from utils import POI_CATEGORIES
    return {
        "categories": POI_CATEGORIES,
        "description": "Available POI categories and their mappings"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
