"""Main trip service - coordinates trip planning operations"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from schemas import TripRequest
from .trip_plan_service import TripPlanService
from .trip_processing_service import TripProcessingService

logger = logging.getLogger(__name__)


class TripService:
    """Main trip service - coordinates all trip operations"""
    
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.plan_service = TripPlanService(db, redis_client)
        self.processing_service = TripProcessingService(db, redis_client)
    
    def create_trip_plan(self, request: TripRequest) -> int:
        """Create trip plan and return trip_id"""
        return self.plan_service.create_trip_plan(request)
    
    async def process_trip_plan(self, trip_id: int, request: TripRequest):
        """Process trip plan in background"""
        await self.processing_service.process_trip_plan(trip_id, request)
    
    def get_trip_detail(self, trip_id: int) -> Optional[Dict]:
        """Get trip plan details"""
        return self.plan_service.get_trip_detail(trip_id)
    
    def get_user_trips(self, user_id: int = 1, limit: int = 10) -> List[Dict]:
        """Get user's trip plan list"""
        return self.plan_service.get_user_trips(user_id, limit)
