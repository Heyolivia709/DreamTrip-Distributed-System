import logging
from typing import Optional

import googlemaps
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings

logger = logging.getLogger(__name__)


class Dependencies:
    """Dependency manager class"""
    
    _gmaps_client: Optional[googlemaps.Client] = None
    _redis_client: Optional[redis.Redis] = None
    _engine = None
    _SessionLocal = None
    
    @classmethod
    def get_gmaps_client(cls) -> Optional[googlemaps.Client]:
        """Get Google Maps client"""
        if cls._gmaps_client is None and settings.google_maps_api_key:
            try:
                cls._gmaps_client = googlemaps.Client(
                    key=settings.google_maps_api_key
                )
                logger.info("Google Maps client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
        return cls._gmaps_client
    
    @classmethod
    def get_redis_client(cls) -> redis.Redis:
        """Get Redis client"""
        if cls._redis_client is None:
            cls._redis_client = redis.Redis.from_url(settings.redis_url)
            logger.info("Redis client initialized")
        return cls._redis_client
    
    @classmethod
    def get_db_session(cls) -> Session:
        """Get database session"""
        if cls._engine is None:
            cls._engine = create_engine(settings.database_url)
            cls._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)
            logger.info("Database engine initialized")
        return cls._SessionLocal()


def get_gmaps() -> Optional[googlemaps.Client]:
    """Dependency injection: Google Maps client"""
    return Dependencies.get_gmaps_client()


def get_redis() -> redis.Redis:
    """Dependency injection: Redis client"""
    return Dependencies.get_redis_client()


def get_db() -> Session:
    """Dependency injection: Database session"""
    db = Dependencies.get_db_session()
    try:
        yield db
    finally:
        db.close()

