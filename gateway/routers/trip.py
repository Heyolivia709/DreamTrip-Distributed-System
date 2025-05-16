"""旅行计划路由"""
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from schemas import TripRequest, TripResponse
from services import TripService
from dependencies import get_db, get_redis


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Trip"])


@router.post("/trip/plan", response_model=TripResponse)
async def create_trip_plan(
    request: TripRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Create 旅行计划
    
    1. 立即返回 trip_id 和 status=processing
    2. 在后台异步调用各个微服务处理数据
    
    Args:
        request: 旅行计划请求（Origin、Destination、Preferences、 days数）
        background_tasks: FastAPI 后台任务
        db: Database session
        redis_client: Redis client
        
    Returns:
        TripResponse: 包含 trip_id 和初始Status
    """
    # Create service instance
    trip_service = TripService(db, redis_client)
    
    # 1. 创建旅行计划并获取 trip_id
    trip_id = trip_service.create_trip_plan(request)
    
    # 2. 添加后台任务处理旅行计划
    background_tasks.add_task(trip_service.process_trip_plan, trip_id, request)
    
    # 3. 立即返回响应
    return TripResponse(
        trip_id=trip_id,
        status="processing"
    )


@router.get("/trip/{trip_id}", response_model=TripResponse)
async def get_trip_plan(
    trip_id: int,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Get 旅行计划详情
    
    先从 Redis 缓存获取，如果没有则从数据库查询
    
    Args:
        trip_id: Trip plan ID
        db: Database session
        redis_client: Redis client
        
    Returns:
        TripResponse: 完整的旅行计划数据
        
    Raises:
        HTTPException: 404 如果旅行计划不存在
    """
    # Create service instance
    trip_service = TripService(db, redis_client)
    
    # 获取旅行计划
    trip_data = trip_service.get_trip_detail(trip_id)
    
    if trip_data is None:
        raise HTTPException(status_code=404, detail="Trip plan not found")
    
    return TripResponse(**trip_data)


@router.get("/trips")
async def get_user_trips(
    user_id: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Get 用户的旅行计划列表
    
    先从数据库查询，如果失败则从 Redis 缓存获取
    
    Args:
        user_id: User ID（默认为1）
        limit: 返回数量限制（默认为10）
        db: Database session
        redis_client: Redis client
        
    Returns:
        旅行计划列表
    """
    # Create service instance
    trip_service = TripService(db, redis_client)
    
    # 获取用户旅行列表
    trips = trip_service.get_user_trips(user_id, limit)
    
    return {"trips": trips}

