"""
Weather Service - 工具函数
"""
import random
from datetime import datetime, timedelta
from typing import List

from models import WeatherForecast, WeatherResponse


#  daysweather条件映射
WEATHER_CONDITIONS = [
    "sunny", "partly_cloudy", "cloudy", "rainy", "stormy",
    "snowy", "foggy", "windy", "hot", "cold"
]

WEATHER_DESCRIPTIONS = {
    "sunny": "晴朗，适合户外活动",
    "partly_cloudy": "部分多云， daysweather宜人",
    "cloudy": "多云，可能有阵雨",
    "rainy": "有雨，建议携带雨具",
    "stormy": "雷雨 daysweather，注意安全",
    "snowy": "降雪，路面湿滑",
    "foggy": "有雾，能见度较低",
    "windy": "风力较大",
    "hot": " daysweather炎热，注意防暑",
    "cold": " daysweather寒冷，注意保暖"
}


def generate_mock_weather(location: str, duration: int) -> WeatherResponse:
    """Generate 模拟 daysweather数据"""
    
    forecast = []
    today = datetime.now().date()
    
    for i in range(duration):
        target_date = today + timedelta(days=i)
        
        # 生成随机 daysweather数据
        condition = random.choice(WEATHER_CONDITIONS)
        temp_min = round(random.uniform(-5, 25), 1)
        temp_max = round(temp_min + random.uniform(5, 15), 1)
        humidity = random.randint(30, 90)
        wind_speed = round(random.uniform(0, 20), 1)
        
        forecast.append(WeatherForecast(
            date=target_date.isoformat(),
            temperature_min=temp_min,
            temperature_max=temp_max,
            condition=condition,
            humidity=humidity,
            wind_speed=wind_speed,
            description=WEATHER_DESCRIPTIONS.get(condition, "Good weather conditions")
        ))
    
    # 生成当前 daysweather
    current_condition = random.choice(WEATHER_CONDITIONS)
    current_temp = round(random.uniform(-5, 35), 1)
    
    current_weather = {
        "temperature": current_temp,
        "condition": current_condition,
        "humidity": random.randint(30, 90),
        "wind_speed": round(random.uniform(0, 20), 1),
        "description": WEATHER_DESCRIPTIONS.get(current_condition, " daysweather条件良好")
    }
    
    return WeatherResponse(
        location=location,
        forecast=forecast,
        current_weather=current_weather
    )


def generate_mock_current_weather(location: str) -> dict:
    """Generate 模拟当前 daysweather"""
    condition = random.choice(WEATHER_CONDITIONS)
    return {
        "location": location,
        "temperature": round(random.uniform(-5, 35), 1),
        "condition": condition,
        "humidity": random.randint(30, 90),
        "wind_speed": round(random.uniform(0, 20), 1),
        "pressure": random.randint(1000, 1030),
        "visibility": round(random.uniform(5, 20), 1),
        "description": WEATHER_DESCRIPTIONS.get(condition, " daysweather条件良好")
    }


def generate_weather_recommendations(condition: str, temperature: float, activity: str) -> List[str]:
    """根据 daysweather条件生成建议"""
    recommendations = []
    
    if "rain" in condition.lower() or "storm" in condition.lower():
        recommendations.append("建议携带雨具或选择室内活动")
    
    if temperature < 5:
        recommendations.append(" daysweather较冷，建议多穿衣服")
    elif temperature > 30:
        recommendations.append(" daysweather炎热，注意防暑降温")
    
    if activity == "outdoor":
        if "sunny" in condition.lower():
            recommendations.append(" daysweather晴朗，适合户外活动，注意防晒")
        elif "rain" in condition.lower():
            recommendations.append("有雨，建议选择室内活动")
    elif activity == "hiking":
        if "fog" in condition.lower():
            recommendations.append("有雾，徒步时注意安全")
        if "wind" in condition.lower():
            recommendations.append("风力较大，注意安全")
    
    return recommendations

