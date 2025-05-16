from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AI Summary Service Configuration"""
    
    # Database configuration
    database_url: str = "postgresql://postgres:password@localhost:5432/dream_trip"
    redis_url: str = "redis://localhost:6379"
    
    # Google Gemini API
    google_ai_api_key: str = ""
    
    @property
    def gemini_api_key(self) -> str:
        return self.google_ai_api_key
    
    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore other service config fields in .env
        env_prefix = ""  # No prefix for environment variables


settings = Settings()
