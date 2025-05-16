"""Dream Trip API Gateway - Application Entry Point

Modular FastAPI application with three-tier architecture:
- routers/: Handle HTTP requests
- services/: Business logic
- repositories/: Database operations
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import health_router, trip_router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("🚀 Starting Dream Trip API Gateway...")
    logger.info("📁 Modular architecture loaded:")
    logger.info("  - routers/: API endpoints")
    logger.info("  - services/: Business logic")
    logger.info("  - repositories/: Data access")
    yield
    logger.info("👋 Shutting down Dream Trip API Gateway...")


app = FastAPI(
    title="Dream Trip API Gateway",
    description="Distributed Travel Planning System Gateway - Modular Architecture",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(trip_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
