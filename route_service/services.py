"""
Route Service - Business Logic Layer
"""
import json
import logging
from typing import Optional, List

import googlemaps
import redis

from models import RouteRequest, RouteResponse, Place

logger = logging.getLogger(__name__)


class RouteService:
    """Route planning service class"""
    
    def __init__(self, gmaps_client: Optional[googlemaps.Client], redis_client: redis.Redis):
        self.gmaps = gmaps_client
        self.redis = redis_client
    
    def get_route(self, request: RouteRequest) -> RouteResponse:
        """Get route planning"""
        
        # Check cache
        cache_key = f"route:{request.origin}:{request.destination}:{request.mode}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Route cache hit for {cache_key}")
            return RouteResponse(**json.loads(cached_result))
        
        # Get route data
        if not self.gmaps:
            raise Exception("Google Maps API key not configured")
        
        try:
            result = self._get_route_from_google_maps(request)
        except Exception as e:
            logger.error(f"Google Maps API error: {e}")
            raise Exception(f"Failed to get route: {e}")
        
        # Cache result (1 hour)
        self.redis.setex(cache_key, 3600, json.dumps(result.model_dump()))
        
        logger.info(f"Route calculated for {request.origin} to {request.destination}")
        return result
    
    def _get_route_from_google_maps(self, request: RouteRequest) -> RouteResponse:
        """Get route using Google Maps API"""
        
        # Call Google Maps Directions API
        directions_result = self.gmaps.directions(
            request.origin,
            request.destination,
            mode=request.mode,
            avoid=request.avoid or []
        )
        
        if not directions_result:
            raise Exception("No route found")
        
        route = directions_result[0]['legs'][0]
        
        # Extract route info
        distance = route['distance']['text']
        duration = route['duration']['text']
        
        # Extract steps
        steps = []
        polyline = None
        bounds = None
        
        for step in route['steps']:
            steps.append(step['html_instructions'].replace('<b>', '').replace('</b>', ''))
        
        # Get polyline and bounds
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
        """Geocoding - convert address to coordinates"""
        
        cache_key = f"geocode:{address}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Geocode cache hit for {cache_key}")
            return json.loads(cached_result)
        
        if not self.gmaps:
            raise Exception("Google Maps API key not configured")
        
        # Use Google Maps Geocoding API
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
        
        # Cache result (24 hours)
        self.redis.setex(cache_key, 86400, json.dumps(result))
        
        return result
    
    def reverse_geocode(self, lat: float, lng: float) -> dict:
        """Reverse geocoding - convert coordinates to address"""
        
        cache_key = f"reverse_geocode:{lat}:{lng}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Reverse geocode cache hit for {cache_key}")
            return json.loads(cached_result)
        
        if not self.gmaps:
            raise Exception("Google Maps API key not configured")
        
        # Use Google Maps Reverse Geocoding API
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
        
        # Cache result (24 hours)
        self.redis.setex(cache_key, 86400, json.dumps(result))
        
        return result
    
    def get_nearby_places(self, lat: float, lng: float, radius: int, place_type: str) -> List[Place]:
        """Get nearby places"""
        
        cache_key = f"nearby_places:{lat}:{lng}:{radius}:{place_type}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"Nearby places cache hit for {cache_key}")
            places_data = json.loads(cached_result)
            return [Place(**place) for place in places_data]
        
        if not self.gmaps:
            raise Exception("Google Maps API key not configured")
        
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
        
        # Cache result (1 hour)
        places_data = [place.model_dump() for place in places]
        self.redis.setex(cache_key, 3600, json.dumps(places_data))
        
        return places

