"""
AI Summary Service - Business Logic Layer
"""
import json
import logging
from typing import Optional

import redis

from models import AISummaryRequest, AISummaryResponse, DayItinerary
from utils import build_ai_prompt, generate_mock_summary, parse_ai_response

logger = logging.getLogger(__name__)


class AIService:
    """AI Service Class"""
    
    def __init__(self, gemini_client, redis_client: redis.Redis):
        self.client = gemini_client
        self.redis = redis_client
    
    async def generate_summary(self, request: AISummaryRequest) -> AISummaryResponse:
        """Generate AI trip summary"""
        
        # Check cache
        cache_key = f"ai_summary:{request.origin}:{request.destination}:{':'.join(request.preferences)}:{request.duration}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            logger.info(f"AI summary cache hit for {cache_key}")
            data = json.loads(cached_result)
            itinerary = [DayItinerary(**day) for day in data.get("itinerary", [])] if data.get("itinerary") else None
            return AISummaryResponse(
                summary=data["summary"],
                recommendations=data["recommendations"],
                tips=data["tips"],
                itinerary=itinerary
            )
        
        # Generate AI summary
        if self.client:
            try:
                result = await self._generate_with_gemini(request)
            except Exception as e:
                logger.warning(f"Gemini API error, using mock data: {e}")
                result_data = generate_mock_summary(request)
                result = self._convert_to_response(result_data)
        else:
            logger.info("Gemini API key not configured, using mock data")
            result_data = generate_mock_summary(request)
            result = self._convert_to_response(result_data)
        
        # Cache result (24 hours)
        cache_data = {
            "summary": result.summary,
            "recommendations": result.recommendations,
            "tips": result.tips,
            "itinerary": [day.dict() for day in result.itinerary] if result.itinerary else []
        }
        self.redis.setex(cache_key, 86400, json.dumps(cache_data))
        
        logger.info(f"AI summary generated for {request.origin} to {request.destination}")
        return result
    
    async def _generate_with_gemini(self, request: AISummaryRequest) -> AISummaryResponse:
        """Generate trip summary using Gemini"""
        
        # Build prompt
        system_instruction = "You are a professional travel planner who excels at creating personalized travel plans. Please respond with engaging and practical content."
        prompt = build_ai_prompt(request)
        
        # Complete prompt
        full_prompt = f"{system_instruction}\n\n{prompt}"
        
        # Call Gemini API
        response = self.client.generate_content(
            full_prompt,
            generation_config={
                'temperature': 0.7,
                'max_output_tokens': 2048,
            }
        )
        
        ai_content = response.text
        
        # Parse AI response
        summary, recommendations, tips, itinerary = parse_ai_response(ai_content, request)
        
        return AISummaryResponse(
            summary=summary,
            recommendations=recommendations,
            tips=tips,
            itinerary=itinerary
        )
    
    def _convert_to_response(self, data: dict) -> AISummaryResponse:
        """Convert dict to response model"""
        itinerary = [DayItinerary(**day) for day in data.get("itinerary", [])] if data.get("itinerary") else None
        return AISummaryResponse(
            summary=data["summary"],
            recommendations=data["recommendations"],
            tips=data["tips"],
            itinerary=itinerary
        )
    
    async def customize_itinerary(self, request: AISummaryRequest, custom_requirements: str) -> dict:
        """Adjust itinerary based on custom requirements"""
        
        if self.client:
            try:
                system_instruction = "You are a professional travel planner who excels at adjusting itineraries based on user needs."
                prompt = f"""
Based on the following travel information and custom requirements, please adjust the itinerary:

**Original Trip Information:**
- Origin: {request.origin}
- Destination: {request.destination}
- Duration: {request.duration} days
- Preferences: {', '.join(request.preferences)}

**Custom Requirements:**
{custom_requirements}

Please provide adjusted itinerary and recommendations.
"""
                
                full_prompt = f"{system_instruction}\n\n{prompt}"
                
                response = self.client.generate_content(
                    full_prompt,
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 2048,
                    }
                )
                
                customized_content = response.text
                
                return {
                    "original_request": request.dict(),
                    "custom_requirements": custom_requirements,
                    "customized_itinerary": customized_content
                }
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                return self._generate_mock_customization(request, custom_requirements)
        else:
            return self._generate_mock_customization(request, custom_requirements)
    
    def _generate_mock_customization(self, request: AISummaryRequest, custom_requirements: str) -> dict:
        """Generate mock custom adjustments"""
        return {
            "original_request": request.dict(),
            "custom_requirements": custom_requirements,
            "customized_itinerary": f"Based on your request'{custom_requirements}', we have adjusted the itinerary.Detailed adjustments will be provided after actual deployment."
        }

