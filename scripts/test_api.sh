#!/bin/bash

# Dream Trip distributed system API test script

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

# Success/failure count
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
test_endpoint "Gateway Health Check" "GET" "http://204.236.144.38:8000/health" "" "healthy"

# Test each microservice
test_endpoint "Route Service Health Check" "GET" "http://204.236.144.38:8001/health" "" "healthy"
test_endpoint "Weather Service Health Check" "GET" "http://204.236.144.38:8002/health" "" "healthy"
test_endpoint "POI Service Health Check" "GET" "http://204.236.144.38:8003/health" "" "healthy"
test_endpoint "AI Summary Service Health Check" "GET" "http://204.236.144.38:8004/health" "" "healthy"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 2: Core Business Process Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test create trip plan
echo -e "${BLUE}[TEST]${NC} Create trip plan (Beijing → Shanghai)"
TRIP_RESPONSE=$(curl -s -X POST http://204.236.144.38:8000/api/trip/plan \
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
    echo -e "${YELLOW}[WAIT]${NC} Waiting for background trip plan processing (8 seconds)..."
    sleep 8
    
           # Test get trip details
           echo ""
           test_endpoint "Get trip plan details" "GET" "http://204.236.144.38:8000/api/trip/$TRIP_ID" "" "completed"
    
else
    echo -e "   ${RED}✗ FAIL${NC} - Unable to create trip plan"
    ((FAILED++))
fi

echo ""
# Test get trip list
test_endpoint "Get user trip list" "GET" "http://204.236.144.38:8000/api/trips?user_id=1&limit=5" "" "trips"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Phase 3: Direct Microservice Call Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test Route Service
test_endpoint "Route Service - Route Planning" "POST" "http://204.236.144.38:8001/route" \
  '{"origin": "Shenzhen", "destination": "Guangzhou"}' "distance"

# Test Weather Service
test_endpoint "Weather Service - Weather Forecast" "POST" "http://204.236.144.38:8002/weather/forecast" \
  '{"location": "Beijing", "duration": 3}' "forecast"

# Test POI Service
test_endpoint "POI Service - POI Recommendations" "POST" "http://204.236.144.38:8003/poi/recommendations" \
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
    echo "🎉 Distributed system running normally!"
    exit 0
else
    echo "⚠️  Please check failed services"
    exit 1
fi

