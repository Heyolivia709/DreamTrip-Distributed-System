"""
AI Summary Service - 依赖注入
"""
import logging
from typing import Optional

import google.generativeai as genai
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings

logger = logging.getLogger(__name__)


class Dependencies:
    """Dependency manager class"""
    
    _gemini_client = None
    _redis_client: Optional[redis.Redis] = None
    _engine = None
    _SessionLocal = None
    
    @classmethod
    def get_gemini_client(cls):
        """Get Gemini client"""
        if cls._gemini_client is None and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                cls._gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        return cls._gemini_client
    
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


def get_gemini():
    """Dependency injection: Gemini client"""
    return Dependencies.get_gemini_client()


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

