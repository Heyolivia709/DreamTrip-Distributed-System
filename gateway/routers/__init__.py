"""路由模块"""
from .health import router as health_router
from .trip import router as trip_router

__all__ = ["health_router", "trip_router"]

