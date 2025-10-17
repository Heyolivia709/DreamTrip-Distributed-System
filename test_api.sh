#!/bin/bash

# Dream Trip Distributed System API Test Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Dream Trip Distributed Intelligent Travel Planning System - API Test          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Success/failure counters
SUCCESS=0
FAILED=0

# Test function
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
echo "  Phase 1: Service Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test Gateway health check
test_endpoint "Gateway 健康检查" "GET" "http://localhost:8000/health" "" "healthy"

# Test individual microservices
test_endpoint "Route Service 健康检查" "GET" "http://localhost:8001/health" "" "healthy"
test_endpoint "Weather Service 健康检查" "GET" "http://localhost:8002/health" "" "healthy"
test_endpoint "POI Service 健康检查" "GET" "http://localhost:8003/health" "" "healthy"
test_endpoint "AI Summary Service 健康检查" "GET" "http://localhost:8004/health" "" "healthy"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 2: Core Business Process Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test creating travel plan
echo -e "${BLUE}[TEST]${NC} Creating travel plan (Beijing → Shanghai)"
TRIP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Beijing",
    "destination": "Shanghai",
    "preferences": ["food", "history", "culture"],
    "duration": 3
  }')

TRIP_ID=$(echo $TRIP_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['trip_id'])" 2>/dev/null)

if [ ! -z "$TRIP_ID" ]; then
    echo -e "   ${GREEN}✓ PASS${NC} (Trip ID: $TRIP_ID)"
    ((SUCCESS++))
    
    # Wait for background processing
    echo ""
    echo -e "${YELLOW}[WAIT]${NC} Waiting for background travel plan processing (8 seconds)..."
    sleep 8
    
    # Test getting travel details
    echo ""
    test_endpoint "Get travel plan details" "GET" "http://localhost:8000/api/trip/$TRIP_ID" "" "completed"
    
else
    echo -e "   ${RED}✗ FAIL${NC} - Unable to create travel plan"
    ((FAILED++))
fi

echo ""
# Test getting travel list
test_endpoint "Get user travel list" "GET" "http://localhost:8000/api/trips?user_id=1&limit=5" "" "trips"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 3: Direct Microservice Call Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test Route Service
test_endpoint "Route Service - Route Planning" "POST" "http://localhost:8001/route" \
  '{"origin": "Shenzhen", "destination": "Guangzhou"}' "distance"

# Test Weather Service
test_endpoint "Weather Service - Weather Forecast" "POST" "http://localhost:8002/weather/forecast" \
  '{"location": "Beijing", "duration": 3}' "forecast"

# Test POI Service
test_endpoint "POI Service - Attraction Recommendations" "POST" "http://localhost:8003/poi/recommendations" \
  '{"location": "Shanghai", "preferences": ["history"], "duration": 2}' "pois"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Test Results Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL=$((SUCCESS + FAILED))
PASS_RATE=$((SUCCESS * 100 / TOTAL))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

echo ""
echo "Total tests: $TOTAL"
echo -e "Passed: ${GREEN}$SUCCESS${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Pass rate: ${PASS_RATE}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 Distributed system is running normally!"
    exit 0
else
    echo "⚠️  Please check failed services"
    exit 1
fi

