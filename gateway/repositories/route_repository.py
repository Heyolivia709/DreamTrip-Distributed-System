"""Route database operations"""
import logging
from typing import Dict
from sqlalchemy.orm import Session

from models import Route
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class RouteRepository(BaseRepository):
    """Route database operations"""
    
    @staticmethod
    def save_route(db: Session, trip_id: int, route_data: Dict) -> bool:
        """Save route information"""
        def _save():
            route = Route(
                trip_plan_id=trip_id,
                origin=route_data.get("origin"),
                destination=route_data.get("destination"),
                distance=route_data.get("distance"),
                duration=route_data.get("duration"),
                steps=route_data.get("steps", [])
            )
            db.add(route)
            return True
        
        result = BaseRepository._execute_with_rollback(db, _save)
        if result:
            BaseRepository._log_success("Route info saved", trip_id)
        return result is not None
