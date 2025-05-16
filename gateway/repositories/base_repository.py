"""Base repository class with common database operations"""
import logging
from typing import Optional, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common database operations"""
    
    @staticmethod
    def _execute_with_rollback(
        db: Session, operation, *args, **kwargs
    ) -> Optional[Any]:
        """Execute database operation with automatic rollback on error"""
        try:
            result = operation(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.warning(f"Database operation failed: {e}")
            return None
    
    @staticmethod
    def _log_success(operation: str, entity_id: int = None):
        """Log successful database operation"""
        if entity_id:
            logger.info(f"{operation} successful for ID {entity_id}")
        else:
            logger.info(f"{operation} successful")
    
    @staticmethod
    def _log_failure(operation: str, error: Exception):
        """Log failed database operation"""
        logger.warning(f"{operation} failed: {error}")
