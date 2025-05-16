#!/bin/bash

# Dream Trip 分布式系统 API 测试脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Dream Trip 分布式智能旅行规划系统 - API 测试          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 成功/失败计数
SUCCESS=0
FAILED=0

# 测试函数
test_endpoint() {
    local test_name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected=$5
    
    echo -e "${BLUE}[TEST]${NC} $test_name"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        if [ -z "$expected" ] || echo "$body" | grep -q "$expected"; then
            echo -e "   ${GREEN}✓ PASS${NC} (HTTP $http_code)"
            ((SUCCESS++))
            return 0
        else
            echo -e "   ${RED}✗ FAIL${NC} - Expected: $expected"
            echo "   Response: $body"
            ((FAILED++))
            return 1
        fi
    else
        echo -e "   ${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "   Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 1: 服务健康检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试 Gateway 健康检查
test_endpoint "Gateway 健康检查" "GET" "http://localhost:8000/health" "" "healthy"

# 测试各个微服务
test_endpoint "Route Service 健康检查" "GET" "http://localhost:8001/health" "" "healthy"
test_endpoint "Weather Service 健康检查" "GET" "http://localhost:8002/health" "" "healthy"
test_endpoint "POI Service 健康检查" "GET" "http://localhost:8003/health" "" "healthy"
test_endpoint "AI Summary Service 健康检查" "GET" "http://localhost:8004/health" "" "healthy"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 2: 核心业务流程测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试创建旅行计划
echo -e "${BLUE}[TEST]${NC} 创建旅行计划（北京 → 上海）"
TRIP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "北京",
    "destination": "上海",
    "preferences": ["美食", "历史", "文化"],
    "duration": 3
  }')

TRIP_ID=$(echo $TRIP_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['trip_id'])" 2>/dev/null)

if [ ! -z "$TRIP_ID" ]; then
    echo -e "   ${GREEN}✓ PASS${NC} (Trip ID: $TRIP_ID)"
    ((SUCCESS++))
    
    # 等待后台处理
    echo ""
    echo -e "${YELLOW}[WAIT]${NC} 等待后台处理旅行计划（8秒）..."
    sleep 8
    
    # 测试获取旅行详情
    echo ""
    test_endpoint "获取旅行计划详情" "GET" "http://localhost:8000/api/trip/$TRIP_ID" "" "completed"
    
else
    echo -e "   ${RED}✗ FAIL${NC} - 无法创建旅行计划"
    ((FAILED++))
fi

echo ""
# 测试获取旅行列表
test_endpoint "获取用户旅行列表" "GET" "http://localhost:8000/api/trips?user_id=1&limit=5" "" "trips"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 3: 微服务直接调用测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试 Route Service
test_endpoint "Route Service - 路线规划" "POST" "http://localhost:8001/route" \
  '{"origin": "深圳", "destination": "广州"}' "distance"

# 测试 Weather Service
test_endpoint "Weather Service - 天气预报" "POST" "http://localhost:8002/weather/forecast" \
  '{"location": "北京", "duration": 3}' "forecast"

# 测试 POI Service
test_endpoint "POI Service - 景点推荐" "POST" "http://localhost:8003/poi/recommendations" \
  '{"location": "上海", "preferences": ["历史"], "duration": 2}' "pois"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  测试结果汇总"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=$((SUCCESS + FAILED))
PASS_RATE=$((SUCCESS * 100 / TOTAL))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
else
    echo -e "${RED}✗ 部分测试失败${NC}"
fi

echo ""
echo "总测试数：$TOTAL"
echo -e "通过：${GREEN}$SUCCESS${NC}"
echo -e "失败：${RED}$FAILED${NC}"
echo "通过率：${PASS_RATE}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 分布式系统运行正常！"
    exit 0
else
    echo "⚠️  请检查失败的服务"
    exit 1
fi

