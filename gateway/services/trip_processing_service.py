"""Trip plan processing service - handles background processing"""
import asyncio
import logging
from typing import Dict
from sqlalchemy.orm import Session

from schemas import TripRequest
from repositories import TripRepository, RouteRepository, WeatherRepository, POIRepository, AIRepository
from .service_client import service_client
from .kafka_producer import kafka_producer

logger = logging.getLogger(__name__)


class TripProcessingService:
    """Handles background trip plan processing"""
    
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.trip_repo = TripRepository()
        self.route_repo = RouteRepository()
        self.weather_repo = WeatherRepository()
        self.poi_repo = POIRepository()
        self.ai_repo = AIRepository()
    
    async def process_trip_plan(self, trip_id: int, request: TripRequest):
        """Process trip plan in background"""
        try:
            logger.info(f"Starting background processing for trip {trip_id}")
            
            # Update status to processing
            self._update_trip_status(trip_id, "processing")
            
            # Process all services in parallel
            tasks = [
                self._get_route_info(trip_id, request),
                self._get_weather_info(trip_id, request),
                self._get_poi_recommendations(trip_id, request)
            ]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if any task failed
            failed_tasks = [i for i, result in enumerate(results) if isinstance(result, Exception)]
            if failed_tasks:
                logger.warning(f"Some tasks failed for trip {trip_id}: {failed_tasks}")
                self._update_trip_status(trip_id, "partial")
            else:
                logger.info(f"All services completed for trip {trip_id}")
                self._update_trip_status(trip_id, "completed")
            
            # Generate AI summary
            try:
                await self._generate_ai_summary(trip_id, request)
            except Exception as e:
                logger.error(f"AI summary generation failed for trip {trip_id}: {e}")
            
            # Send Kafka event
            try:
                await kafka_producer.send_trip_completed_event(trip_id, request)
            except Exception as e:
                logger.error(f"Failed to send Kafka event for trip {trip_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error processing trip {trip_id}: {e}")
            self._update_trip_status(trip_id, "failed")
            raise
    
    async def _get_route_info(self, trip_id: int, request: TripRequest) -> Dict:
        """Get route information"""
        try:
            data = {
                "origin": request.origin,
                "destination": request.destination
            }
            result = await service_client.call_service("route", "/route", data)
            
            # Try to save to database
            self.route_repo.save_route(self.db, trip_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting route info for trip {trip_id}: {e}")
            raise
    
    async def _get_weather_info(self, trip_id: int, request: TripRequest) -> Dict:
        """Get weather information"""
        try:
            data = {
                "location": request.destination,
                "duration": request.duration
            }
            result = await service_client.call_service("weather", "/weather/forecast", data)
            
            # Try to save to database
            self.weather_repo.save_weather_forecasts(
                self.db, trip_id, request.destination, result.get("forecast", [])
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting weather info for trip {trip_id}: {e}")
            raise
    
    async def _get_poi_recommendations(self, trip_id: int, request: TripRequest) -> Dict:
        """Get POI recommendations"""
        try:
            data = {
                "location": request.destination,
                "preferences": request.preferences,
                "duration": request.duration
            }
            result = await service_client.call_service("poi", "/poi/recommendations", data)
            
            # Try to save to database
            self.poi_repo.save_pois(self.db, trip_id, result.get("pois", []))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting POI recommendations for trip {trip_id}: {e}")
            raise
    
    async def _generate_ai_summary(self, trip_id: int, request: TripRequest) -> Dict:
        """Generate AI summary"""
        try:
            # Get all collected data
            route_result = await self._get_route_info(trip_id, request)
            weather_result = await self._get_weather_info(trip_id, request)
            poi_result = await self._get_poi_recommendations(trip_id, request)
            
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
            
            # Try to save AI Summary to database
            self.ai_repo.save_ai_summary(self.db, trip_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI summary for trip {trip_id}: {e}")
            raise
    
    def _update_trip_status(self, trip_id: int, status: str):
        """Update trip plan status"""
        self.trip_repo.update_trip_status(self.db, trip_id, status)
