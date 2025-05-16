import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """路线服务配置"""
    
    # Database configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/dream_trip"
    redis_url: str = "redis://localhost:6379"
    
    # Google Maps API
    google_maps_api_key: str = ""
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore other service config fields in .env

settings = Settings()


