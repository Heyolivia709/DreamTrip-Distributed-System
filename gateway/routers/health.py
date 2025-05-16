"""Health check endpoints"""
from datetime import datetime
from fastapi import APIRouter

from services import service_client


router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Dream Trip API Gateway is running"}


@router.get("/health")
async def health_check():
    """Health check with microservice status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check all microservices
    for service_name in ["route", "weather", "poi", "ai"]:
        status = await service_client.check_service_health(service_name)
        health_status["services"][service_name] = status
    
    return health_status

