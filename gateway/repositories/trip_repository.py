"""Trip plan database operations"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from models import TripPlan
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TripRepository(BaseRepository):
    """Trip plan database operations"""
    
    @staticmethod
    def create_trip_plan(
        db: Session,
        user_id: int,
        origin: str,
        destination: str,
        preferences: List[str],
        duration: int
    ) -> Optional[TripPlan]:
        """Create trip plan"""
        def _create():
            trip_plan = TripPlan(
                user_id=user_id,
                origin=origin,
                destination=destination,
                preferences=preferences,
                duration=duration,
                status="processing"
            )
            db.add(trip_plan)
            db.flush()  # Get ID without committing
            return trip_plan
        
        result = BaseRepository._execute_with_rollback(db, _create)
        if result:
            BaseRepository._log_success("Created trip plan", result.id)
        return result
    
    @staticmethod
    def update_trip_status(db: Session, trip_id: int, status: str) -> bool:
        """Update trip plan status"""
        def _update():
            trip = db.query(TripPlan).filter(TripPlan.id == trip_id).first()
            if trip:
                trip.status = status
                return True
            return False
        
        result = BaseRepository._execute_with_rollback(db, _update)
        if result:
            BaseRepository._log_success("Updated trip status", trip_id)
        return result is not None
    
    @staticmethod
    def get_trip_plan(db: Session, trip_id: int) -> Optional[dict]:
        """Get trip plan with all related data"""
        try:
            query = text("""
                SELECT 
                    tp.id, tp.user_id, tp.origin, tp.destination, 
                    tp.preferences, tp.duration, tp.status, tp.created_at,
                    r.distance, r.duration as route_duration, r.steps,
                    json_agg(DISTINCT jsonb_build_object(
                        'date', wf.date,
                        'temperature_min', wf.temperature_min,
                        'temperature_max', wf.temperature_max,
                        'condition', wf.condition,
                        'humidity', wf.humidity,
                        'wind_speed', wf.wind_speed
                    )) FILTER (WHERE wf.id IS NOT NULL) as weather,
                    json_agg(DISTINCT jsonb_build_object(
                        'name', p.name,
                        'category', p.category,
                        'rating', p.rating,
                        'address', p.address,
                        'latitude', p.latitude,
                        'longitude', p.longitude,
                        'description', p.description
                    )) FILTER (WHERE p.id IS NOT NULL) as pois,
                    ai.summary, ai.recommendations, ai.tips
                FROM trip_plans tp
                LEFT JOIN routes r ON tp.id = r.trip_plan_id
                LEFT JOIN weather_forecasts wf ON tp.id = wf.trip_plan_id
                LEFT JOIN pois p ON tp.id = p.trip_plan_id
                LEFT JOIN ai_summaries ai ON tp.id = ai.trip_plan_id
                WHERE tp.id = :trip_id
                GROUP BY tp.id, r.id, ai.id
            """)
            
            result = db.execute(query, {"trip_id": trip_id}).fetchone()
            return result
        except Exception as e:
            BaseRepository._log_failure("Get trip plan", e)
            return None
    
    @staticmethod
    def get_user_trips(db: Session, user_id: int = 1, limit: int = 10) -> List:
        """Get user's trip plan list"""
        try:
            query = text("""
                SELECT id, origin, destination, status, created_at
                FROM trip_plans
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            results = db.execute(
                query, 
                {"user_id": user_id, "limit": limit}
            ).fetchall()
            return results
        except Exception as e:
            BaseRepository._log_failure("Get user trips", e)
            return []