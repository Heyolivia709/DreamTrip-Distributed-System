"""
POI Service - 工具函数
"""
import random
from typing import List

from models import POI


# POI类别映射
POI_CATEGORIES = {
    "美食": "restaurant",
    "购物": "shopping_mall",
    "文化": "museum",
    "自然": "park",
    "历史": "tourist_attraction",
    "娱乐": "amusement_park",
    "夜生活": "night_club",
    "宗教": "place_of_worship",
    "冒险": "tourist_attraction",
    "艺术": "art_gallery"
}

# 模拟POI数据
MOCK_POIS = {
    "restaurant": [
        {"name": "老北京烤鸭店", "rating": 4.8, "description": "正宗北京烤鸭，皮脆肉嫩"},
        {"name": "蜀香川菜馆", "rating": 4.5, "description": "地道川菜，麻辣鲜香"},
        {"name": "江南小笼包", "rating": 4.6, "description": "精致小笼包，汤汁鲜美"},
    ],
    "museum": [
        {"name": "国家博物馆", "rating": 4.9, "description": "中国历史文化展览"},
        {"name": "现代艺术馆", "rating": 4.7, "description": "当代艺术作品展示"},
        {"name": "科技馆", "rating": 4.6, "description": "互动科技体验"},
    ],
    "park": [
        {"name": "中央公园", "rating": 4.7, "description": "城市绿肺，休闲好去处"},
        {"name": "植物园", "rating": 4.6, "description": "各类植物，四季花卉"},
        {"name": "森林公园", "rating": 4.8, "description": "自然生态，空weather清新"},
    ],
    "tourist_attraction": [
        {"name": "古城墙", "rating": 4.8, "description": "历史遗迹，文化传承"},
        {"name": "古镇水乡", "rating": 4.7, "description": "江南水乡，古韵悠长"},
        {"name": "名胜风景区", "rating": 4.9, "description": "自然风光，景色优美"},
    ],
    "shopping_mall": [
        {"name": "国际购物中心", "rating": 4.5, "description": "国际品牌，一站式购物"},
        {"name": "步行街", "rating": 4.4, "description": "特色商铺，美食小吃"},
        {"name": "奥特莱斯", "rating": 4.6, "description": "名牌折扣，物美价廉"},
    ]
}


def map_preferences_to_categories(preferences: List[str]) -> List[str]:
    """将用户Preferences映射到 Google Places 类别"""
    categories = []
    for pref in preferences:
        if pref in POI_CATEGORIES:
            categories.append(POI_CATEGORIES[pref])
        else:
            # 默认使用 tourist_attraction
            categories.append("tourist_attraction")
    
    # 去重
    return list(set(categories))


def generate_mock_pois(location: str, preferences: List[str]) -> List[POI]:
    """Generate 模拟POI数据"""
    categories = map_preferences_to_categories(preferences)
    
    pois = []
    for category in categories:
        # 从模拟数据中随机选择
        if category in MOCK_POIS:
            mock_data = random.sample(MOCK_POIS[category], min(2, len(MOCK_POIS[category])))
        else:
            # 如果没有对应类别，使用默认数据
            mock_data = [
                {"name": f"Mock {category} 1", "rating": round(random.uniform(4.0, 5.0), 1), "description": f"A nice {category}"},
                {"name": f"Mock {category} 2", "rating": round(random.uniform(4.0, 5.0), 1), "description": f"Another {category}"}
            ]
        
        for data in mock_data:
            pois.append(POI(
                name=data["name"],
                category=category,
                rating=data["rating"],
                address=f"{location}, Mock Street",
                description=data["description"],
                latitude=round(random.uniform(39.0, 41.0), 6),
                longitude=round(random.uniform(115.0, 117.0), 6),
                opening_hours="09:00-18:00",
                price_level=random.randint(1, 4)
            ))
    
    return pois


def generate_mock_place_details(place_id: str) -> dict:
    """Generate 模拟地点详情"""
    return {
        "name": f"Place {place_id}",
        "rating": round(random.uniform(4.0, 5.0), 1),
        "address": "Mock Address",
        "phone": "+86 123-4567-8900",
        "website": "https://example.com",
        "opening_hours": ["Monday: 09:00 - 18:00", "Tuesday: 09:00 - 18:00"],
        "reviews": [
            {"author": "User1", "rating": 5, "text": "Great place!"},
            {"author": "User2", "rating": 4, "text": "Nice experience"}
        ]
    }

