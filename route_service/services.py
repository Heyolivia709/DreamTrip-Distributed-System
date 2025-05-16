"""
Route Service - Business Logic Layer
"""
import json
import logging
from typing import Optional, List

import googlemaps
import redis

from models import RouteRequest, RouteResponse, Place
from utils import (
    generate_mock_route,
    generate_mock_geocoding,
    generate_mock_reverse_geocoding,
    generate_mock_nearby_places
)

logger = logging.getLogger(__name__)


class RouteService:
    """路线规划服务类"""
    
    def __init__(self, gmaps_client: Optional[googlemaps.Client], redis_client: redis.Redis):
        self.gmaps = gmaps_client
        self.redis = redis_client
    
    def get_route(self, request: RouteRequest) -> RouteResponse:
        """Get 路线规划"""
        
        # Check cache
        cache_key = f"route:{request.origin}:{request.destination}:{request.mode}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Route cache hit for {cache_key}")
            return RouteResponse(**json.loads(cached_result))
        
        # 获取路线数据
        if self.gmaps:
            try:
                result = self._get_route_from_google_maps(request)
            except Exception as e:
                logger.warning(f"Google Maps API error, using mock data: {e}")
                result = generate_mock_route(request)
        else:
            logger.info("Google Maps API key not configured, using mock data")
            result = generate_mock_route(request)
        
        # Cache result (1 hour)
        self.redis.setex(cache_key, 3600, json.dumps(result.dict()))
        
        logger.info(f"Route calculated for {request.origin} to {request.destination}")
        return result
    
    def _get_route_from_google_maps(self, request: RouteRequest) -> RouteResponse:
        """使用 Google Maps API 获取路线"""
        
        # 调用Google Maps Directions API
        directions_result = self.gmaps.directions(
            request.origin,
            request.destination,
            mode=request.mode,
            avoid=request.avoid or []
        )
        
        if not directions_result:
            raise Exception("No route found")
        
        route = directions_result[0]['legs'][0]
        
        # 提取Route info
        distance = route['distance']['text']
        duration = route['duration']['text']
        
        # 提取步骤
        steps = []
        polyline = None
        bounds = None
        
        for step in route['steps']:
            steps.append(step['html_instructions'].replace('<b>', '').replace('</b>', ''))
        
        # 获取polyline和bounds
        if 'overview_polyline' in directions_result[0]:
            polyline = directions_result[0]['overview_polyline']['points']
        
        if 'bounds' in directions_result[0]:
            bounds = directions_result[0]['bounds']
        
        return RouteResponse(
            origin=request.origin,
            destination=request.destination,
            distance=distance,
            duration=duration,
            steps=steps,
            polyline=polyline,
            bounds=bounds
        )
    
    def geocode(self, address: str) -> dict:
        """地理编码 - 将地址转换为坐标"""
        
        cache_key = f"geocode:{address}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Geocode cache hit for {cache_key}")
            return json.loads(cached_result)
        
        if self.gmaps:
            # 使用Google Maps Geocoding API
            geocode_result = self.gmaps.geocode(address)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                result = {
                    "address": address,
                    "latitude": location['lat'],
                    "longitude": location['lng'],
                    "formatted_address": geocode_result[0]['formatted_address']
                }
            else:
                raise Exception("Address not found")
        else:
            # 模拟地理编码
            result = generate_mock_geocoding(address)
        
        # Cache result (24 hours)
        self.redis.setex(cache_key, 86400, json.dumps(result))
        
        return result
    
    def reverse_geocode(self, lat: float, lng: float) -> dict:
        """反向地理编码 - 将坐标转换为地址"""
        
        cache_key = f"reverse_geocode:{lat}:{lng}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Reverse geocode cache hit for {cache_key}")
            return json.loads(cached_result)
        
        if self.gmaps:
            # 使用Google Maps Reverse Geocoding API
            reverse_geocode_result = self.gmaps.reverse_geocode((lat, lng))
            
            if reverse_geocode_result:
                result = {
                    "latitude": lat,
                    "longitude": lng,
                    "address": reverse_geocode_result[0]['formatted_address'],
                    "components": reverse_geocode_result[0].get('address_components', [])
                }
            else:
                raise Exception("Location not found")
        else:
            # 模拟反向地理编码
            result = generate_mock_reverse_geocoding(lat, lng)
        
        # Cache result (24 hours)
        self.redis.setex(cache_key, 86400, json.dumps(result))
        
        return result
    
    def get_nearby_places(self, lat: float, lng: float, radius: int, place_type: str) -> List[Place]:
        """Get 附近地点"""
        
        cache_key = f"nearby_places:{lat}:{lng}:{radius}:{place_type}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Nearby places cache hit for {cache_key}")
            places_data = json.loads(cached_result)
            return [Place(**place) for place in places_data]
        
        if self.gmaps:
            # 使用Google Places API
            places_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type=place_type
            )
            
            places = []
            for place in places_result.get('results', []):
                places.append(Place(
                    name=place.get('name'),
                    place_id=place.get('place_id'),
                    rating=place.get('rating'),
                    vicinity=place.get('vicinity'),
                    types=place.get('types', []),
                    geometry=place.get('geometry', {})
                ))
        else:
            # 模拟附近地点
            places = generate_mock_nearby_places()
        
        # Cache result (1 hour)
        places_data = [place.dict() for place in places]
        self.redis.setex(cache_key, 3600, json.dumps(places_data))
        
        return places

