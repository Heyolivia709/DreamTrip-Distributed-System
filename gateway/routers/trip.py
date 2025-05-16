"""Trip planning routes"""
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from schemas import TripRequest, TripResponse
from services import TripService
from dependencies import get_db, get_redis


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Trip"])


@router.post("/trip/plan", response_model=TripResponse)
async def create_trip_plan(
    request: TripRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), redis_client=Depends(get_redis)
):
    """Create trip plan
    
    1. Immediately return trip_id and status=processing
    2. Asynchronously call microservices in background to process data
    
    Args:
        request: Trip plan request (Origin, Destination, Preferences, duration)
        background_tasks: FastAPI background tasks
        db: Database session
        redis_client: Redis client
        
    Returns:
        TripResponse: Contains trip_id and initial status
    """
    # Create service instance
    trip_service = TripService(db, redis_client)
    
    # 1. Create trip plan and get trip_id
    trip_id = trip_service.create_trip_plan(request)
    
    # 2. Add background task to process trip plan
    background_tasks.add_task(trip_service.process_trip_plan, trip_id, request)
    
    # 3. Return response immediately
    return TripResponse(
        trip_id=trip_id,
        status="processing"
    )


@router.get("/trip/{trip_id}", response_model=TripResponse)
async def get_trip_plan(
    trip_id: int,
    db: Session = Depends(get_db), redis_client=Depends(get_redis)
):
    """Get trip plan details
    
    First try Redis cache, then query database if not found
    
    Args:
        trip_id: Trip plan ID
        db: Database session
        redis_client: Redis client
        
    Returns:
        TripResponse: Complete trip plan data
        
    Raises:
        HTTPException: 404 if trip plan doesn't exist
    """
    # Create service instance
    trip_service = TripService(db, redis_client)
    
    # Get trip plan
    trip_data = trip_service.get_trip_detail(trip_id)
    
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip plan not found")
    
    return TripResponse(**trip_data)


@router.get("/trips")
async def get_user_trips(
    user_id: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db), redis_client=Depends(get_redis)
):
    """Get user's trip plan list
    
    First query database, fallback to Redis cache if failed
    
    Args:
        user_id: User ID (default: 1)
        limit: Return count limit (default: 10)
        db: Database session
        redis_client: Redis client
        
    Returns:
        List of trip plans
    """
    # Create service instance
    trip_service = TripService(db, redis_client)
    
    # Get user trip list
    trips = trip_service.get_user_trips(user_id, limit)
    
    return {"trips": trips}

