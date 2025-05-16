"""AI Summary database operations"""
import logging
from typing import Dict
from sqlalchemy.orm import Session

from models import AISummary
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AIRepository(BaseRepository):
    """AI Summary database operations"""
    
    @staticmethod
    def save_ai_summary(db: Session, trip_id: int, summary_data: Dict) -> bool:
        """Save AI summary"""
        def _save():
            ai_summary = AISummary(
                trip_plan_id=trip_id,
                summary=summary_data.get("summary"),
                recommendations=summary_data.get("recommendations"),
                tips=summary_data.get("tips")
            )
            db.add(ai_summary)
            return True
        
        result = BaseRepository._execute_with_rollback(db, _save)
        if result:
            BaseRepository._log_success("AI summary saved", trip_id)
        return result is not None
