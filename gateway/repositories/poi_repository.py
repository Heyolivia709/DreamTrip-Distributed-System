"""POI database operations"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session

from models import POI
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class POIRepository(BaseRepository):
    """POI database operations"""
    
    @staticmethod
    def save_pois(db: Session, trip_id: int, pois: List[Dict]) -> bool:
        """Save POI information"""
        def _save():
            for poi_data in pois:
                poi = POI(
                    trip_plan_id=trip_id,
                    name=poi_data["name"],
                    category=poi_data.get("category"),
                    rating=poi_data.get("rating"),
                    address=poi_data.get("address"),
                    latitude=poi_data.get("latitude"),
                    longitude=poi_data.get("longitude"),
                    description=poi_data.get("description"),
                    price_level=poi_data.get("price_level")
                )
                db.add(poi)
            return True
        
        result = BaseRepository._execute_with_rollback(db, _save)
        if result:
            BaseRepository._log_success("POI info saved", trip_id)
        return result is not None
