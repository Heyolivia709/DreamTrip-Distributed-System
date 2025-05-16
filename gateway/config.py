import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """网关服务配置"""
    
    # Database configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/dream_trip"
    redis_url: str = "redis://localhost:6379"
    
    # Kafka配置
    kafka_broker: str = "localhost:9092"
    
    # 微服务URL
    route_service_url: str = "http://localhost:8001"
    weather_service_url: str = "http://localhost:8002"
    poi_service_url: str = "http://localhost:8003"
    ai_service_url: str = "http://localhost:8004"
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore other service config fields in .env


settings = Settings()


