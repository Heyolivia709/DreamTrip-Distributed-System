"""Trip plan creation and management service"""
import json
import logging
import time
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from schemas import TripRequest
from repositories import TripRepository

logger = logging.getLogger(__name__)


class TripPlanService:
    """Trip plan creation and management"""
    
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.trip_repo = TripRepository()
    
    def create_trip_plan(self, request: TripRequest) -> int:
        """Create trip plan and return trip_id"""
        # Try to save to database
        trip_plan = self.trip_repo.create_trip_plan(
            self.db,
            user_id=request.user_id,
            origin=request.origin,
            destination=request.destination,
            preferences=request.preferences,
            duration=request.duration
        )
        
        if trip_plan:
            trip_id = trip_plan.id
        else:
            # If database unavailable, use timestamp as temporary ID
            trip_id = int(time.time())
            logger.warning(f"Database unavailable, using temporary ID: {trip_id}")
        
        logger.info(f"Created trip plan {trip_id} for {request.origin} to {request.destination}")
        return trip_id
    
    def update_trip_status(self, trip_id: int, status: str):
        """Update trip plan status"""
        self.trip_repo.update_trip_status(self.db, trip_id, status)
    
    def get_trip_detail(self, trip_id: int) -> Optional[Dict]:
        """Get trip plan details with caching"""
        # 1. First check Redis cache
        cache_key = f"trip_detail:{trip_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            logger.info(f"Trip {trip_id} found in Redis cache")
            return json.loads(cached_data)
        
        # 2. If not in cache, get from database
        result = self.trip_repo.get_trip_plan(self.db, trip_id)
        
        if result:
            # Build response data
            trip_data = {
                "trip_id": result.id,
                "user_id": result.user_id,
                "origin": result.origin,
                "destination": result.destination,
                "preferences": result.preferences,
                "duration": result.duration,
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None,
                "route": {
                    "distance": result.distance,
                    "duration": result.route_duration,
                    "steps": result.steps
                } if result.distance else None,
                "weather": result.weather if result.weather else [],
                "pois": result.pois if result.pois else [],
                "ai_summary": {
                    "summary": result.summary,
                    "recommendations": result.recommendations,
                    "tips": result.tips
                } if result.summary else None
            }
            
            # Cache for 1 hour
            self.redis.setex(cache_key, 3600, json.dumps(trip_data))
            logger.info(f"Trip {trip_id} cached in Redis")
            
            return trip_data
        else:
            logger.warning(f"Trip {trip_id} not found")
            return None
    
    def get_user_trips(self, user_id: int = 1, limit: int = 10) -> List[Dict]:
        """Get user's trip plan list"""
        # 1. Try to get from database
        results = self.trip_repo.get_user_trips(self.db, user_id, limit)
        
        if results:
            trips = []
            for row in results:
                trips.append({
                    "trip_id": row.id,
                    "origin": row.origin,
                    "destination": row.destination,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })
            return trips
        else:
            logger.warning(f"No trips found for user {user_id}")
            return []
