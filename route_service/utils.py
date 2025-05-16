"""
Route Service - 工具函数
"""
import random
from typing import List

from models import RouteRequest, RouteResponse, Place


def generate_mock_route(request: RouteRequest) -> RouteResponse:
    """Generate 模拟路线数据"""
    
    # 模拟距离和时间
    distances = ["50 km", "120 km", "85 km", "200 km", "150 km"]
    durations = ["1h 15m", "2h 30m", "1h 45m", "3h 20m", "2h 10m"]
    
    distance = random.choice(distances)
    duration = random.choice(durations)
    
    # 生成模拟步骤
    steps = [
        f"Start from {request.origin}",
        "Continue on Main Street",
        "Take the highway entrance",
        f"Follow signs for {request.destination}",
        "Take exit toward city center",
        f"Arrive at {request.destination}"
    ]
    
    return RouteResponse(
        origin=request.origin,
        destination=request.destination,
        distance=distance,
        duration=duration,
        steps=steps
    )


def generate_mock_geocoding(address: str) -> dict:
    """Generate 模拟地理编码数据"""
    return {
        "address": address,
        "latitude": round(random.uniform(39.0, 41.0), 6),
        "longitude": round(random.uniform(115.0, 117.0), 6),
        "formatted_address": f"{address}, China"
    }


def generate_mock_reverse_geocoding(lat: float, lng: float) -> dict:
    """Generate 模拟反向地理编码数据"""
    return {
        "latitude": lat,
        "longitude": lng,
        "address": f"Mock Address at {lat}, {lng}",
        "components": []
    }


def generate_mock_nearby_places() -> List[Place]:
    """Generate 模拟附近地点数据"""
    mock_places_data = [
        {"name": "Famous Museum", "rating": 4.5, "vicinity": "Nearby Area"},
        {"name": "Historic Temple", "rating": 4.2, "vicinity": "Nearby Area"},
        {"name": "Scenic Park", "rating": 4.7, "vicinity": "Nearby Area"},
        {"name": "Local Restaurant", "rating": 4.0, "vicinity": "Nearby Area"},
        {"name": "Shopping Center", "rating": 3.8, "vicinity": "Nearby Area"}
    ]
    
    selected = random.sample(mock_places_data, min(3, len(mock_places_data)))
    return [Place(**place) for place in selected]

