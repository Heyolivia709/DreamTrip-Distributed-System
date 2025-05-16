"""
AI Summary Service - AI Text Summarization
"""
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from models import AISummaryRequest, AISummaryResponse
from services import AIService
from dependencies import get_gemini, get_redis, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Summary Service", description="AI Text Summarization Service")


@app.get("/")
async def root():
    """Health check"""
    return {"message": "AI Summary Service is running", "timestamp": datetime.now().isoformat()}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with details"""
    client = get_gemini()
    redis_client = get_redis()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini": "available" if client else "unavailable",
            "redis": "unknown",
            "database": "unknown"
        }
    }
    
    # Check Redis connection
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "available"
    except Exception as e:
        health_status["services"]["redis"] = f"unavailable: {str(e)[:50]}"
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "available"
    except Exception as e:
        health_status["services"]["database"] = f"unavailable: {str(e)[:50]}"
    
    return health_status


@app.post("/ai/summarize", response_model=AISummaryResponse)
async def generate_ai_summary(request: AISummaryRequest):
    """Generate AI trip summary"""
    try:
        service = AIService(get_gemini(), get_redis())
        return await service.generate_summary(request)
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI summary: {str(e)}")


@app.get("/ai/templates")
async def get_summary_templates():
    """Get summary template"""
    return {
        "templates": {
            "nature": "Nature exploration journey",
            "food": "Food culture experience journey",
            "adventure": "Exciting adventure challenge journey",
            "art": "Art and culture immersion journey"
        },
        "preferences": ["nature", "food", "adventure", "art", "shopping", "nightlife", "history", "religion"]
    }


@app.post("/ai/customize")
async def customize_itinerary(request: AISummaryRequest, custom_requirements: str):
    """Adjust itinerary based on custom requirements"""
    try:
        service = AIService(get_gemini(), get_redis())
        return await service.customize_itinerary(request, custom_requirements)
    except Exception as e:
        logger.error(f"Error customizing itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to customize itinerary: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
