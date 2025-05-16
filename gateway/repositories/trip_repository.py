"""数据库访问层 - 旅行计划相关的数据库操作"""
import logging
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from models import TripPlan, Route, WeatherForecast, POI, AISummary


logger = logging.getLogger(__name__)


class TripRepository:
    """旅行计划数据库操作"""
    
    @staticmethod
    def create_trip_plan(
        db: Session,
        user_id: int,
        origin: str,
        destination: str,
        preferences: List[str],
        duration: int
    ) -> Optional[TripPlan]:
        """Create 旅行计划
        
        Returns:
            TripPlan 对象，如果失败返回 None
        """
        try:
            trip_plan = TripPlan(
                user_id=user_id,
                origin=origin,
                destination=destination,
                preferences=preferences,
                duration=duration,
                status="processing"
            )
            db.add(trip_plan)
            db.commit()
            db.refresh(trip_plan)
            logger.info(f"Created trip plan {trip_plan.id}")
            return trip_plan
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to create trip plan: {e}")
            return None
    
    @staticmethod
    def update_trip_status(db: Session, trip_id: int, status: str) -> bool:
        """Update 旅行计划Status
        
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            trip = db.query(TripPlan).filter(TripPlan.id == trip_id).first()
            if trip:
                trip.status = status
                db.commit()
                logger.info(f"Updated trip {trip_id} status to {status}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to update trip status: {e}")
            return False
    
    @staticmethod
    def save_route(db: Session, trip_id: int, route_data: Dict) -> bool:
        """Save Route info"""
        try:
            route = Route(
                trip_plan_id=trip_id,
                origin=route_data.get("origin"),
                destination=route_data.get("destination"),
                distance=route_data.get("distance"),
                duration=route_data.get("duration"),
                steps=route_data.get("steps", [])
            )
            db.add(route)
            db.commit()
            logger.info(f"Route info saved for trip {trip_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to save route: {e}")
            return False
    
    @staticmethod
    def save_weather_forecasts(
        db: Session, 
        trip_id: int, 
        location: str, 
        forecasts: List[Dict]
    ) -> bool:
        """Save  daysweather预报信息"""
        try:
            for day_weather in forecasts:
                weather = WeatherForecast(
                    trip_plan_id=trip_id,
                    location=location,
                    date=day_weather["date"],
                    temperature_min=day_weather.get("temp_min"),
                    temperature_max=day_weather.get("temp_max"),
                    condition=day_weather.get("condition"),
                    humidity=day_weather.get("humidity"),
                    wind_speed=day_weather.get("wind_speed")
                )
                db.add(weather)
            db.commit()
            logger.info(f"Weather info saved for trip {trip_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to save weather: {e}")
            return False
    
    @staticmethod
    def save_pois(db: Session, trip_id: int, pois: List[Dict]) -> bool:
        """Save POI info"""
        try:
            for poi_data in pois:
                poi = POI(
                    trip_plan_id=trip_id,
                    name=poi_data["name"],
                    category=poi_data.get("category"),
                    rating=poi_data.get("rating"),
                    address=poi_data.get("address"),
                    latitude=poi_data.get("latitude"),
                    longitude=poi_data.get("longitude"),
                    description=poi_data.get("description"),
                    price_level=poi_data.get("price_level")
                )
                db.add(poi)
            db.commit()
            logger.info(f"POI info saved for trip {trip_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to save POIs: {e}")
            return False
    
    @staticmethod
    def save_ai_summary(db: Session, trip_id: int, summary_data: Dict) -> bool:
        """Save AISummary"""
        try:
            ai_summary = AISummary(
                trip_plan_id=trip_id,
                summary=summary_data.get("summary"),
                recommendations=summary_data.get("recommendations"),
                tips=summary_data.get("tips")
            )
            db.add(ai_summary)
            db.commit()
            logger.info(f"AI summary saved for trip {trip_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to save AI summary: {e}")
            return False
    
    @staticmethod
    def get_trip_plan(db: Session, trip_id: int) -> Optional[TripPlan]:
        """Get 旅行计划"""
        try:
            query = text("""
                SELECT 
                    tp.id, tp.user_id, tp.origin, tp.destination, 
                    tp.preferences, tp.duration, tp.status, tp.created_at,
                    r.distance, r.duration as route_duration, r.steps,
                    json_agg(DISTINCT jsonb_build_object(
                        'date', wf.date,
                        'temperature_min', wf.temperature_min,
                        'temperature_max', wf.temperature_max,
                        'condition', wf.condition,
                        'humidity', wf.humidity,
                        'wind_speed', wf.wind_speed
                    )) FILTER (WHERE wf.id IS NOT NULL) as weather,
                    json_agg(DISTINCT jsonb_build_object(
                        'name', p.name,
                        'category', p.category,
                        'rating', p.rating,
                        'address', p.address,
                        'latitude', p.latitude,
                        'longitude', p.longitude,
                        'description', p.description
                    )) FILTER (WHERE p.id IS NOT NULL) as pois,
                    ai.summary, ai.recommendations, ai.tips
                FROM trip_plans tp
                LEFT JOIN routes r ON tp.id = r.trip_plan_id
                LEFT JOIN weather_forecasts wf ON tp.id = wf.trip_plan_id
                LEFT JOIN pois p ON tp.id = p.trip_plan_id
                LEFT JOIN ai_summaries ai ON tp.id = ai.trip_plan_id
                WHERE tp.id = :trip_id
                GROUP BY tp.id, r.id, ai.id
            """)
            
            result = db.execute(query, {"trip_id": trip_id}).fetchone()
            return result
        except Exception as e:
            logger.warning(f"Failed to get trip plan: {e}")
            return None
    
    @staticmethod
    def get_user_trips(db: Session, user_id: int = 1, limit: int = 10) -> List:
        """Get 用户的旅行计划列表"""
        try:
            query = text("""
                SELECT id, origin, destination, status, created_at
                FROM trip_plans
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            results = db.execute(
                query, 
                {"user_id": user_id, "limit": limit}
            ).fetchall()
            return results
        except Exception as e:
            logger.warning(f"Failed to get user trips: {e}")
            return []

