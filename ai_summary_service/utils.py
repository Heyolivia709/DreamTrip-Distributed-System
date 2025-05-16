"""
AI Summary Service - Utility Functions
"""
from typing import List
from models import AISummaryRequest, DayItinerary


# Destination information mapping
DESTINATION_INFO = {
    "Beijing": "Capital Beijing, with profound historical and cultural heritage. Must-visit: Forbidden City, Great Wall, Temple of Heaven. Special food: Beijing Roast Duck, Zhajiangmian.",
    "Shanghai": "International metropolis, perfect blend of modern and traditional. Must-visit: The Bund, Oriental Pearl Tower, Yu Garden. Special food: Xiaolongbao, Shengjianbao.",
    "Hangzhou": "Paradise on earth, typical representative of Jiangnan water town. Must-visit: West Lake, Lingyin Temple, Leifeng Pagoda. Special food: West Lake Fish in Vinegar, Longjing Shrimp.",
    "Chengdu": "Land of abundance, leisure capital, hometown of pandas. Must-visit: Giant Panda Base, Kuanzhai Alley, Jinli. Special food: Hot Pot, Chuanchuan.",
    "Xi'an": "Ancient capital Chang'an, starting point of the Silk Road. Must-visit: Terracotta Warriors, Big Wild Goose Pagoda, Ancient City Wall. Special food: Roujiamo, Liangpi, Yangrou Paomo."
}

# Preference keywords mapping
PREFERENCE_KEYWORDS = {
    "nature": ["natural scenery", "eco-tourism", "outdoor activities", "fresh air"],
    "food": ["local cuisine", "local snacks", "food experience", "culinary delight"],
    "adventure": ["exciting experience", "challenge yourself", "adventure activities", "adrenaline"],
    "art": ["art and culture", "historical sites", "art exhibitions", "cultural immersion"],
    "history": ["historical relics", "cultural heritage", "ancient site visits", "historical stories"]
}


def get_destination_info(destination: str) -> str:
    """Get destination features"""
    return DESTINATION_INFO.get(destination, f"{destination} is a charming tourist destination")


def build_ai_prompt(request: AISummaryRequest) -> str:
    """Build AI prompt"""
    
    destination_info = get_destination_info(request.destination)
    
    prompt = f"""
You are a senior travel planner. Please generate a professional, detailed, and personalized travel plan and summary for the following travel information:

**Basic Travel Information:**
- Origin: {request.origin}
- Destination: {request.destination}
- Duration: {request.duration} days
- Preferences: {', '.join(request.preferences)}

**Destination Features:**
{destination_info}
"""
    
    if request.route:
        prompt += f"\n**Transportation Route:**\nDistance: {request.route.get('distance')}, Time: {request.route.get('duration')}\n"
    
    if request.weather:
        prompt += "\n**Weather Forecast:**\n"
        for day in request.weather[:3]:
            prompt += f"- {day.get('date')}: {day.get('condition')}, {day.get('temperature_min')}°C - {day.get('temperature_max')}°C\n"
    
    if request.pois:
        prompt += "\n**Recommended Attractions:**\n"
        for poi in request.pois[:5]:
            prompt += f"- {poi.get('name')} ({poi.get('category')}): Rating {poi.get('rating')}/5 stars\n"
    
    prompt += f"""
Based on the above information, please provide for this {request.duration}-day traveler from {request.origin} to {request.destination}:

**1. Trip Highlights Summary** (2-3 paragraphs)
**2. Personalized Recommendations** (based on user preferences)
**3. Practical Travel Tips** (transportation, accommodation, precautions)
**4. Detailed Daily Itinerary** (specific and actionable)

Please reply in English, with vivid and interesting language, practical and specific content.
"""
    
    return prompt


def generate_mock_itinerary(request: AISummaryRequest) -> List[DayItinerary]:
    """Generate mock itinerary"""
    
    itinerary = []
    
    for day in range(1, request.duration + 1):
        day_plan = DayItinerary(
            day=day,
            title=f"Day {day}",
            activities=[]
        )
        
        if day == 1:
            day_plan.activities = [
                f"Morning: Depart from {request.origin}",
                "Afternoon: Arrive at destination, check into hotel",
                "Evening: Taste local cuisine"
            ]
        elif day == request.duration:
            day_plan.activities = [
                "Morning: Final sightseeing",
                "Afternoon: Buy souvenirs",
                f"Evening: Return to {request.origin}"
            ]
        else:
            day_plan.activities = [
                "Morning: Visit main attractions",
                "Afternoon: Experience local culture",
                "Evening: Free time"
            ]
        
        itinerary.append(day_plan)
    
    return itinerary


def generate_mock_summary(request: AISummaryRequest) -> dict:
    """Generate mock AI summary"""
    
    # Build personalized summary
    summary = f"This is an exciting {request.duration}-day trip from {request.origin} to {request.destination}."
    summary += get_destination_info(request.destination)
    
    # Add preference-related descriptions
    summary_keywords = []
    for pref in request.preferences:
        summary_keywords.extend(PREFERENCE_KEYWORDS.get(pref, []))
    
    if summary_keywords:
        summary += f"You will experience colorful activities such as {', '.join(summary_keywords[:3])}."
    summary += "This trip will bring you unforgettable experiences and precious memories."
    
    # Generate recommendations
    recommendations = "Based on your preferences, we especially recommend:\n"
    for pref in request.preferences:
        if pref == "nature":
            recommendations += "- Visit local natural parks, enjoy fresh air and beautiful scenery\n"
        elif pref == "food":
            recommendations += "- Taste local specialties, experience authentic flavors\n"
        elif pref == "adventure":
            recommendations += "- Participate in exciting outdoor activities, challenge yourself\n"
        elif pref == "art" or pref == "history":
            recommendations += "- Visit museums and historical sites, feel the cultural charm\n"
    
    # Generate tips
    tips = "Travel tips:\n"
    tips += "- Book hotels and attraction tickets in advance\n"
    tips += "- Prepare clothes suitable for local weather\n"
    tips += "- Bring common medicines and charging devices\n"
    tips += "- Learn about local transportation and payment methods\n"
    tips += "- Keep an open mind and enjoy the journey\n"
    
    # Generate itinerary
    itinerary = generate_mock_itinerary(request)
    
    return {
        "summary": summary,
        "recommendations": recommendations,
        "tips": tips,
        "itinerary": [day.model_dump() for day in itinerary]
    }


def parse_ai_response(content: str, request: AISummaryRequest) -> tuple:
    """Parse AI response"""
    
    lines = content.split('\n')
    summary = ""
    recommendations = ""
    tips = ""
    itinerary = []
    
    current_section = ""
    current_day = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Section recognition
        if any(keyword in line for keyword in ["Trip Highlights", "Summary"]):
            current_section = "summary"
            continue
        elif any(keyword in line for keyword in ["Recommendations", "Suggested Activities"]):
            current_section = "recommendations"
            continue
        elif any(keyword in line for keyword in ["Practical", "Precautions", "Travel Tips"]):
            current_section = "tips"
            continue
        elif any(keyword in line for keyword in ["Itinerary", "Daily Schedule"]):
            current_section = "itinerary"
            continue
        elif line.startswith("Day") and "day" in line:
            current_section = "itinerary"
            current_day = DayItinerary(
                day=len(itinerary) + 1,
                title=line,
                activities=[]
            )
            itinerary.append(current_day)
            continue
        
        # Process content
        if current_section == "summary" and not line.startswith("**"):
            summary += line + " "
        elif current_section == "recommendations" and not line.startswith("**"):
            if line.startswith("-") or line.startswith("•"):
                recommendations += line[1:].strip() + "\n"
            else:
                recommendations += line + "\n"
        elif current_section == "tips" and not line.startswith("**"):
            if line.startswith("-") or line.startswith("•"):
                tips += line[1:].strip() + "\n"
            else:
                tips += line + "\n"
        elif current_section == "itinerary" and current_day:
            if line.startswith("-") or line.startswith("•"):
                current_day.activities.append(line[1:].strip())
    
    # If no content is parsed, use default values
    if not summary:
        summary = content[:500] if len(content) > 500 else content
    if not itinerary:
        itinerary = generate_mock_itinerary(request)
    
    return summary.strip(), recommendations.strip(), tips.strip(), itinerary

