"""
Route Service - Route Planning
"""
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from models import RouteRequest, RouteResponse, NearbyPlacesResponse
from services import RouteService
from dependencies import get_gmaps, get_redis, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Route Service", description="Route Planning Service")


@app.get("/")
async def root():
    """Health check"""
    return {"message": "Route Service is running", "timestamp": datetime.now().isoformat()}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with details"""
    gmaps = get_gmaps()
    redis_client = get_redis()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "google_maps": "available" if gmaps else "unavailable",
            "redis": "available" if redis_client.ping() else "unavailable",
            "database": "unknown"
        }
    }
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "available"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
    
    return health_status


@app.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    """Get route planning"""
    try:
        service = RouteService(get_gmaps(), get_redis())
        return service.get_route(request)
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate route: {str(e)}")


@app.get("/geocode")
async def geocode_address(address: str):
    """Geocoding - convert address to coordinates"""
    try:
        service = RouteService(get_gmaps(), get_redis())
        return service.geocode(address)
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")


@app.get("/reverse-geocode")
async def reverse_geocode(lat: float, lng: float):
    """Reverse geocoding - convert coordinates to address"""
    try:
        service = RouteService(get_gmaps(), get_redis())
        return service.reverse_geocode(lat, lng)
    except Exception as e:
        logger.error(f"Reverse geocoding error: {e}")
        raise HTTPException(status_code=500, detail=f"Reverse geocoding failed: {str(e)}")


@app.get("/nearby-places", response_model=NearbyPlacesResponse)
async def get_nearby_places(
    lat: float, 
    lng: float, 
    radius: int = 5000, 
    place_type: str = "tourist_attraction"
):
    """Get nearby places"""
    try:
        service = RouteService(get_gmaps(), get_redis())
        places = service.get_nearby_places(lat, lng, radius, place_type)
        return NearbyPlacesResponse(places=places)
    except Exception as e:
        logger.error(f"Nearby places error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get nearby places: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
