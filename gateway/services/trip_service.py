"""旅行计划业务逻辑服务"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from schemas import TripRequest
from repositories import TripRepository
from .service_client import service_client
from .kafka_producer import kafka_producer


logger = logging.getLogger(__name__)


class TripService:
    """旅行计划业务逻辑"""
    
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.repository = TripRepository()
    
    def create_trip_plan(self, request: TripRequest) -> int:
        """Create 旅行计划并返回 trip_id
        
        Args:
            request: 旅行计划请求
            
        Returns:
            trip_id
        """
        # Try to save to database
        trip_plan = self.repository.create_trip_plan(
            self.db,
            user_id=request.user_id,
            origin=request.origin,
            destination=request.destination,
            preferences=request.preferences,
            duration=request.duration
        )
        
        if trip_plan:
            trip_id = trip_plan.id
        else:
            # 如果数据库不可用，使用时间戳作为临时ID
            trip_id = int(time.time() * 1000)
            logger.info(f"Using temporary trip_id: {trip_id} (no database)")
        
        # 发送 Kafka 事件
        kafka_producer.send_trip_created_event(trip_id, {
            "origin": request.origin,
            "destination": request.destination,
            "duration": request.duration,
            "preferences": request.preferences
        })
        
        return trip_id
    
    async def process_trip_plan(self, trip_id: int, request: TripRequest):
        """后台处理旅行计划 - 调用各个微服务并聚合结果
        
        Args:
            trip_id: Trip plan ID
            request: 旅行计划请求
        """
        logger.info(f"Processing trip plan {trip_id}")
        
        try:
            # 并行调用各个服务
            tasks = [
                self._get_route_info(trip_id, request),
                self._get_weather_info(trip_id, request),
                self._get_poi_recommendations(trip_id, request)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 提取结果
            route_result = results[0] if not isinstance(results[0], Exception) else None
            weather_result = results[1] if not isinstance(results[1], Exception) else None
            poi_result = results[2] if not isinstance(results[2], Exception) else None
            
            # 检查结果并生成AISummary
            if all(not isinstance(result, Exception) for result in results):
                ai_result = await self._generate_ai_summary(
                    trip_id, request, route_result, weather_result, poi_result
                )
                
                # 保存完整的旅行计划到 Redis
                trip_data = {
                    "trip_id": trip_id,
                    "status": "completed",
                    "origin": request.origin,
                    "destination": request.destination,
                    "preferences": request.preferences,
                    "duration": request.duration,
                    "route": route_result,
                    "weather": weather_result.get("forecast", []) if weather_result else [],
                    "pois": poi_result.get("pois", []) if poi_result else [],
                    "ai_summary": ai_result
                }
                self.redis.setex(f"trip:{trip_id}", 86400, json.dumps(trip_data))
                
                self._update_trip_status(trip_id, "completed")
                
                # 发送 Kafka 事件
                kafka_producer.send_trip_completed_event(trip_id)
                
                logger.info(f"Trip plan {trip_id} completed and cached")
            else:
                self._update_trip_status(trip_id, "failed")
                
                # 发送 Kafka 事件
                kafka_producer.send_trip_failed_event(trip_id, "One or more services failed")
                
                logger.error(f"Failed to process trip plan {trip_id}")
                
        except Exception as e:
            logger.error(f"Error processing trip plan {trip_id}: {e}")
            self._update_trip_status(trip_id, "failed")
            
            # 发送 Kafka 事件
            kafka_producer.send_trip_failed_event(trip_id, str(e))
    
    async def _get_route_info(self, trip_id: int, request: TripRequest) -> Dict:
        """Get Route info"""
        try:
            data = {
                "origin": request.origin,
                "destination": request.destination
            }
            result = await service_client.call_service("route", "/route", data)
            
            # Try to save to database
            self.repository.save_route(self.db, trip_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting route info for trip {trip_id}: {e}")
            raise
    
    async def _get_weather_info(self, trip_id: int, request: TripRequest) -> Dict:
        """Get  daysweather信息"""
        try:
            data = {
                "location": request.destination,
                "duration": request.duration
            }
            result = await service_client.call_service("weather", "/weather/forecast", data)
            
            # Try to save to database
            self.repository.save_weather_forecasts(
                self.db, trip_id, request.destination, result.get("forecast", [])
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting weather info for trip {trip_id}: {e}")
            raise
    
    async def _get_poi_recommendations(self, trip_id: int, request: TripRequest) -> Dict:
        """Get 景点推荐"""
        try:
            data = {
                "location": request.destination,
                "preferences": request.preferences,
                "duration": request.duration
            }
            result = await service_client.call_service("poi", "/poi/recommendations", data)
            
            # Try to save to database
            self.repository.save_pois(self.db, trip_id, result.get("pois", []))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting POI recommendations for trip {trip_id}: {e}")
            raise
    
    async def _generate_ai_summary(
        self, 
        trip_id: int, 
        request: TripRequest,
        route_result: Dict,
        weather_result: Dict,
        poi_result: Dict
    ) -> Dict:
        """Generate AISummary"""
        try:
            data = {
                "origin": request.origin,
                "destination": request.destination,
                "preferences": request.preferences,
                "duration": request.duration,
                "route": route_result,
                "weather": weather_result.get("forecast", []) if weather_result else [],
                "pois": poi_result.get("pois", []) if poi_result else []
            }
            
            result = await service_client.call_service("ai", "/ai/summarize", data)
            
            # 尝试保存AISummary到数据库
            self.repository.save_ai_summary(self.db, trip_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI summary for trip {trip_id}: {e}")
            raise
    
    def _update_trip_status(self, trip_id: int, status: str):
        """Update 旅行计划Status"""
        self.repository.update_trip_status(self.db, trip_id, status)
    
    def get_trip_detail(self, trip_id: int) -> Optional[Dict]:
        """Get 旅行计划详情
        
        先从 Redis 缓存查找，如果没有则从数据库查询
        
        Args:
            trip_id: Trip plan ID
            
        Returns:
            旅行计划详情，如果不存在返回 None
        """
        # 1. 先从 Redis 缓存中获取
        cache_key = f"trip:{trip_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            logger.info(f"Trip {trip_id} found in Redis cache")
            return json.loads(cached_data)
        
        # 2. 如果缓存中没有，从数据库获取
        result = self.repository.get_trip_plan(self.db, trip_id)
        
        if result:
            # 构建响应数据
            trip_data = {
                "trip_id": result.id,
                "status": result.status,
                "origin": result.origin,
                "destination": result.destination,
                "route": {
                    "origin": result.origin,
                    "destination": result.destination,
                    "distance": result.distance,
                    "duration": result.route_duration,
                    "steps": result.steps or []
                } if result.distance else None,
                "weather": result.weather or [],
                "pois": result.pois or [],
                "ai_summary": {
                    "summary": result.summary,
                    "recommendations": result.recommendations,
                    "tips": result.tips
                } if result.summary else None
            }
            
            logger.info(f"Trip {trip_id} found in database")
            return trip_data
        
        # 3. 数据库中也没有
        logger.info(f"Trip {trip_id} not found")
        return None
    
    def get_user_trips(self, user_id: int = 1, limit: int = 10) -> List[Dict]:
        """Get 用户的旅行计划列表
        
        先从数据库查询，如果失败则从 Redis 获取最近的行程
        
        Args:
            user_id: User ID
            limit: 返回数量限制
            
        Returns:
            旅行计划列表
        """
        # 1. 尝试从数据库获取
        results = self.repository.get_user_trips(self.db, user_id, limit)
        
        if results:
            trips = []
            for row in results:
                trips.append({
                    "trip_id": row.id,
                    "origin": row.origin,
                    "destination": row.destination,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })
            logger.info(f"Found {len(trips)} trips from database for user {user_id}")
            return trips
        
        # 2. 如果数据库不可用，尝试从 Redis 获取最近的行程
        logger.info("Database unavailable, fetching recent trips from Redis cache")
        trips = []
        
        try:
            # 扫描 Redis 中的 trip:* 键
            for key in self.redis.scan_iter("trip:*", count=100):
                if len(trips) >= limit:
                    break
                
                cached_data = self.redis.get(key)
                if cached_data:
                    trip_data = json.loads(cached_data)
                    trips.append({
                        "trip_id": trip_data.get("trip_id"),
                        "origin": trip_data.get("origin"),
                        "destination": trip_data.get("destination"),
                        "status": trip_data.get("status", "completed"),
                        "created_at": None
                    })
            
            logger.info(f"Found {len(trips)} trips from Redis cache")
            return trips[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching trips from Redis: {e}")
            return []

