"""
Weather Service - Utility Functions
"""
from typing import List


def generate_weather_recommendations(condition: str, temperature: float, activity: str) -> List[str]:
    """Generate recommendations based on weather conditions"""
    recommendations = []
    
    if "rain" in condition.lower() or "storm" in condition.lower():
        recommendations.append("Recommend bringing rain gear or choosing indoor activities")
    
    if temperature < 5:
        recommendations.append("Weather is cold, recommend wearing more clothes")
    elif temperature > 30:
        recommendations.append("Weather is hot, stay cool and hydrated")
    
    if activity == "outdoor":
        if "sunny" in condition.lower():
            recommendations.append("Weather is sunny, suitable for outdoor activities, use sunscreen")
        elif "rain" in condition.lower():
            recommendations.append("Rainy weather, recommend indoor activities")
    elif activity == "hiking":
        if "fog" in condition.lower():
            recommendations.append("Foggy conditions, be careful when hiking")
        if "wind" in condition.lower():
            recommendations.append("Strong winds, stay safe")
    
    return recommendations

