"""微服务客户端 - 负责调用其他服务"""
import logging
import httpx
from fastapi import HTTPException

from config import settings


logger = logging.getLogger(__name__)


class ServiceClient:
    """微服务客户端"""
    
    def __init__(self):
        self.service_urls = {
            "route": settings.route_service_url,
            "weather": settings.weather_service_url,
            "poi": settings.poi_service_url,
            "ai": settings.ai_service_url
        }
    
    async def call_service(self, service_name: str, endpoint: str, data: dict) -> dict:
        """Call 微服务
        
        Args:
            service_name: 服务名称 (route/weather/poi/ai)
            endpoint: API端点路径
            data: 请求数据
            
        Returns:
            服务响应数据
            
        Raises:
            HTTPException: 服务调用失败
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
        """Check 服务健康Status
        
        Args:
            service_name: 服务名称
            
        Returns:
            "healthy" 或 "unhealthy"
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

