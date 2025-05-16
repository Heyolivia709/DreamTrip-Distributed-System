"""Microservice client - responsible for calling other services"""
import logging
import httpx
from fastapi import HTTPException

from config import settings


logger = logging.getLogger(__name__)


class ServiceClient:
    """Microservice client"""
    
    def __init__(self):
        self.service_urls = {
            "route": settings.route_service_url,
            "weather": settings.weather_service_url,
            "poi": settings.poi_service_url,
            "ai": settings.ai_service_url
        }
    
    async def call_service(self, service_name: str, endpoint: str, data: dict) -> dict:
        """Call microservice
        
        Args:
            service_name: Service name (route/weather/poi/ai)
            endpoint: API endpoint path
            data: Request data
            
        Returns:
            Service response data
            
        Raises:
            HTTPException: Service call failed
        """
        url = f"{self.service_urls[service_name]}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Service {service_name} request error: {e}")
                raise HTTPException(
                    status_code=503, 
                    detail=f"Service {service_name} unavailable"
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"Service {service_name} HTTP error: {e}")
                raise HTTPException(
                    status_code=e.response.status_code, 
                    detail=f"Service {service_name} error"
                )
    
    async def check_service_health(self, service_name: str) -> str:
        """Check service health status
        
        Args:
            service_name: Service name
            
        Returns:
            "healthy" or "unhealthy"
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.service_urls[service_name]}/health"
                response = await client.get(url, timeout=5.0)
                return "healthy" if response.status_code == 200 else "unhealthy"
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return "unhealthy"


# Singleton
service_client = ServiceClient()

