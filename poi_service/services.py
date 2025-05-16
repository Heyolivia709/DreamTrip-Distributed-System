"""
POI Service - Business Logic Layer
"""
import json
import logging
from typing import Optional, List

import googlemaps
import redis

from models import POIRequest, POI, POIResponse
from utils import map_preferences_to_categories, generate_mock_pois, generate_mock_place_details

logger = logging.getLogger(__name__)


class POIService:
    """POI Service Class"""
    
    def __init__(self, gmaps_client: Optional[googlemaps.Client], redis_client: redis.Redis):
        self.gmaps = gmaps_client
        self.redis = redis_client
    
    async def get_poi_recommendations(self, request: POIRequest) -> POIResponse:
        """Get POI推荐"""
        
        # Check cache
        cache_key = f"poi:{request.location}:{':'.join(sorted(request.preferences))}:{request.radius}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"POI cache hit for {cache_key}")
            data = json.loads(cached_result)
            pois = [POI(**poi) for poi in data["pois"]]
            return POIResponse(location=data["location"], pois=pois, total_count=data["total_count"])
        
        # 获取POI数据
        if self.gmaps:
            try:
                pois = await self._get_pois_from_google_places(request)
            except Exception as e:
                logger.warning(f"Google Places API error, using mock data: {e}")
                pois = generate_mock_pois(request.location, request.preferences)
        else:
            logger.info("Google Places API key not configured, using mock data")
            pois = generate_mock_pois(request.location, request.preferences)
        
        result = POIResponse(
            location=request.location,
            pois=pois,
            total_count=len(pois)
        )
        
        # Cache result (1 hour)
        cache_data = {
            "location": result.location,
            "pois": [poi.dict() for poi in result.pois],
            "total_count": result.total_count
        }
        self.redis.setex(cache_key, 3600, json.dumps(cache_data))
        
        logger.info(f"POI recommendations generated for {request.location}")
        return result
    
    async def _get_pois_from_google_places(self, request: POIRequest) -> List[POI]:
        """使用 Google Places API 获取POI"""
        
        # 先进行地理编码获取坐标
        geocode_result = self.gmaps.geocode(request.location)
        if not geocode_result:
            raise Exception(f"Location not found: {request.location}")
        
        location = geocode_result[0]['geometry']['location']
        lat, lng = location['lat'], location['lng']
        
        # 将用户Preferences映射到 Google Places 类别
        categories = map_preferences_to_categories(request.preferences)
        
        all_pois = []
        for category in categories:
            try:
                # 使用 Google Places API
                places_result = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=request.radius,
                    type=category
                )
                
                # 处理结果
                for place in places_result.get('results', [])[:5]:  # 每个类别最多5个
                    poi = POI(
                        name=place.get('name', 'Unknown'),
                        category=category,
                        rating=place.get('rating', 0.0),
                        address=place.get('vicinity', 'Unknown'),
                        description=place.get('types', [''])[0] if place.get('types') else '',
                        latitude=place.get('geometry', {}).get('location', {}).get('lat'),
                        longitude=place.get('geometry', {}).get('location', {}).get('lng'),
                        photo_url=self._get_photo_url(place.get('photos', [{}])[0]) if place.get('photos') else None,
                        opening_hours=self._format_opening_hours(place.get('opening_hours')),
                        price_level=place.get('price_level')
                    )
                    all_pois.append(poi)
            except Exception as e:
                logger.warning(f"Error getting POIs for category {category}: {e}")
                continue
        
        return all_pois
    
    def _get_photo_url(self, photo: dict) -> Optional[str]:
        """Get 照片URL"""
        if not photo or not self.gmaps:
            return None
        try:
            photo_reference = photo.get('photo_reference')
            if photo_reference:
                return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={self.gmaps.key}"
        except:
            return None
        return None
    
    def _format_opening_hours(self, opening_hours: Optional[dict]) -> Optional[str]:
        """格式化营业时间"""
        if not opening_hours:
            return None
        if opening_hours.get('open_now'):
            return "Currently open"
        return "Closed"
    
    async def get_place_details(self, place_id: str) -> dict:
        """Get 地点详情"""
        
        cache_key = f"place_details:{place_id}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Place details cache hit for {cache_key}")
            return json.loads(cached_result)
        
        if self.gmaps:
            try:
                # 使用 Google Places API
                place_result = self.gmaps.place(place_id)
                result_data = place_result.get('result', {})
                
                result = {
                    "name": result_data.get('name', 'Unknown'),
                    "rating": result_data.get('rating', 0.0),
                    "address": result_data.get('formatted_address', 'Unknown'),
                    "phone": result_data.get('formatted_phone_number'),
                    "website": result_data.get('website'),
                    "opening_hours": result_data.get('opening_hours', {}).get('weekday_text', []),
                    "reviews": [
                        {
                            "author": review.get('author_name'),
                            "rating": review.get('rating'),
                            "text": review.get('text')
                        }
                        for review in result_data.get('reviews', [])[:5]
                    ]
                }
            except Exception as e:
                logger.warning(f"Google Places API error, using mock data: {e}")
                result = generate_mock_place_details(place_id)
        else:
            result = generate_mock_place_details(place_id)
        
        # Cache result (24 hours)
        self.redis.setex(cache_key, 86400, json.dumps(result))
        
        return result

