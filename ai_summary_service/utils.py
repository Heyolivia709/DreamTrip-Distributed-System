"""
AI Summary Service - 工具函数
"""
from typing import List
from models import AISummaryRequest, DayItinerary


# Destination信息映射
DESTINATION_INFO = {
    "北京": "首都北京，拥有深厚的历史文化底蕴。必游：故宫、长城、 days坛。特色美食：北京烤鸭、炸酱面。",
    "上海": "国际化大都市，现代与传统完美融合。必游：外滩、东方明珠、豫园。特色美食：小笼包、生煎包。",
    "杭州": "人间 days堂，江南水乡的典型代表。必游：西湖、灵隐寺、雷峰塔。特色美食：西湖醋鱼、龙井虾仁。",
    "成都": " days府之国，休闲之都，熊猫故乡。必游：大熊猫基地、宽窄巷子、锦里。特色美食：火锅、串串香。",
    "西安": "古都长安，丝绸之路起点。必游：兵马俑、大雁塔、古城墙。特色美食：肉夹馍、凉皮、羊肉泡馍。"
}

# Preferences关键词映射
PREFERENCE_KEYWORDS = {
    "自然": ["自然风光", "生态旅游", "户外活动", "清新空weather"],
    "美食": ["特色美食", "当地小吃", "美食体验", "味蕾享受"],
    "冒险": ["刺激体验", "挑战自我", "探险活动", "肾上腺素"],
    "艺术": ["文化艺术", "历史古迹", "艺术展览", "文化熏陶"],
    "历史": ["历史遗迹", "文化传承", "古迹游览", "历史故事"]
}


def get_destination_info(destination: str) -> str:
    """Get destination features"""
    return DESTINATION_INFO.get(destination, f"{destination}是一个充满魅力的旅游Destination")


def build_ai_prompt(request: AISummaryRequest) -> str:
    """Build AI prompt"""
    
    destination_info = get_destination_info(request.destination)
    
    prompt = f"""
你是一位资深的旅行规划师，请为以下旅行信息生成一份专业、详细、个性化的旅行计划和Summary：

**旅行基本信息：**
- Origin: {request.origin}
- Destination: {request.destination}
- Duration: {request.duration} days
- Preferences: {', '.join(request.preferences)}

**Destination特色：**
{destination_info}
"""
    
    if request.route:
        prompt += f"\n**交通路线：**\n距离：{request.route.get('distance')}，时间：{request.route.get('duration')}\n"
    
    if request.weather:
        prompt += "\n** daysweather预报：**\n"
        for day in request.weather[:3]:
            prompt += f"- {day.get('date')}: {day.get('condition')}, {day.get('temperature_min')}°C - {day.get('temperature_max')}°C\n"
    
    if request.pois:
        prompt += "\n**推荐景点：**\n"
        for poi in request.pois[:5]:
            prompt += f"- {poi.get('name')} ({poi.get('category')}): 评分 {poi.get('rating')}/5星\n"
    
    prompt += f"""
请基于以上信息，为这位从{request.origin}到{request.destination}的{request.duration} days旅行者，提供：

**1. 行程亮点Summary**（2-3段话）
**2. 个性化推荐**（基于用户Preferences）
**3. 实用旅行建议**（交通、住宿、注意事项）
**4. 每日详细行程安排**（具体可操作）

请用中文回复，语言生动有趣，内容实用具体。
"""
    
    return prompt


def generate_mock_itinerary(request: AISummaryRequest) -> List[DayItinerary]:
    """Generate mock itinerary"""
    
    itinerary = []
    
    for day in range(1, request.duration + 1):
        day_plan = DayItinerary(
            day=day,
            title=f"第{day} days",
            activities=[]
        )
        
        if day == 1:
            day_plan.activities = [
                f"上午：从{request.origin}出发",
                "下午：到达Destination，入住酒店",
                "晚上：品尝当地美食"
            ]
        elif day == request.duration:
            day_plan.activities = [
                "上午：最后游览景点",
                "下午：购买纪念品",
                f"晚上：返回{request.origin}"
            ]
        else:
            day_plan.activities = [
                "上午：游览主要景点",
                "下午：体验当地文化",
                "晚上：自由活动"
            ]
        
        itinerary.append(day_plan)
    
    return itinerary


def generate_mock_summary(request: AISummaryRequest) -> dict:
    """Generate mock AI summary"""
    
    # 构建个性化Summary
    summary = f"这是一次从{request.origin}到{request.destination}的{request.duration} days精彩旅行。"
    summary += get_destination_info(request.destination)
    
    # 添加Preferences相关描述
    summary_keywords = []
    for pref in request.preferences:
        summary_keywords.extend(PREFERENCE_KEYWORDS.get(pref, []))
    
    if summary_keywords:
        summary += f"您将体验到{', '.join(summary_keywords[:3])}等丰富多彩的活动。"
    summary += "这次旅行将为您带来难忘的体验和珍贵的回忆。"
    
    # 生成推荐
    recommendations = "基于您的Preferences，我们特别推荐：\n"
    for pref in request.preferences:
        if pref == "自然":
            recommendations += "- 前往当地自然公园，享受清新空weather和美丽风景\n"
        elif pref == "美食":
            recommendations += "- 品尝当地特色美食，体验地道风味\n"
        elif pref == "冒险":
            recommendations += "- 参加刺激的户外活动，挑战自我\n"
        elif pref == "艺术" or pref == "历史":
            recommendations += "- 参观博物馆和历史古迹，感受文化魅力\n"
    
    # 生成建议
    tips = "旅行建议：\n"
    tips += "- 提前预订酒店和景点门票\n"
    tips += "- 准备适合当地weather候的衣物\n"
    tips += "- 携带常用药品和充电设备\n"
    tips += "- 了解当地交通方式和支付方式\n"
    tips += "- 保持开放心态，享受旅程\n"
    
    # 生成行程
    itinerary = generate_mock_itinerary(request)
    
    return {
        "summary": summary,
        "recommendations": recommendations,
        "tips": tips,
        "itinerary": [day.dict() for day in itinerary]
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
        
        # 段落识别
        if any(keyword in line for keyword in ["行程亮点", "Summary"]):
            current_section = "summary"
            continue
        elif any(keyword in line for keyword in ["推荐", "建议活动"]):
            current_section = "recommendations"
            continue
        elif any(keyword in line for keyword in ["实用", "注意事项", "旅行建议"]):
            current_section = "tips"
            continue
        elif any(keyword in line for keyword in ["行程安排", "每日行程"]):
            current_section = "itinerary"
            continue
        elif line.startswith("第") and " days" in line:
            current_section = "itinerary"
            current_day = DayItinerary(
                day=len(itinerary) + 1,
                title=line,
                activities=[]
            )
            itinerary.append(current_day)
            continue
        
        # 处理内容
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
    
    # 如果没有解析到内容，使用默认值
    if not summary:
        summary = content[:500] if len(content) > 500 else content
    if not itinerary:
        itinerary = generate_mock_itinerary(request)
    
    return summary.strip(), recommendations.strip(), tips.strip(), itinerary

