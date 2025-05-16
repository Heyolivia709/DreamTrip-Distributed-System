#!/bin/bash

# Dream Trip startup script
# Usage: ./start.sh

echo "🚀 Starting Dream Trip services..."

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# No log files, output will be displayed directly in terminal

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment does not exist, creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r gateway/requirements.txt
else
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check infrastructure
echo -e "\n${YELLOW}Checking infrastructure...${NC}"

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}❌ Redis is not running${NC}"
    echo -e "   Please start: ${YELLOW}brew services start redis${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Check PostgreSQL
if docker ps | grep -q dream_trip-postgres || pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL may not be running (some features may be limited)${NC}"
fi

# Check Kafka (optional)
if ! nc -z localhost 9092 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Kafka is not running (event-driven features will be unavailable)${NC}"
else
    echo -e "${GREEN}✓ Kafka is running${NC}"
fi

# Start all microservices
echo -e "\n${YELLOW}Starting microservices...${NC}"

# Route Service
cd route_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 &
cd ..
echo -e "${GREEN}✓ Route Service started${NC} (port 8001)"

# Weather Service
cd weather_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 &
cd ..
echo -e "${GREEN}✓ Weather Service started${NC} (port 8002)"

# POI Service
cd poi_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 &
cd ..
echo -e "${GREEN}✓ POI Service started${NC} (port 8003)"

# AI Summary Service
cd ai_summary_service
python3 -m uvicorn main:app --host 0.0.0.0 --port 8004 &
cd ..
echo -e "${GREEN}✓ AI Service started${NC} (port 8004)"

# Wait for microservices to start
echo -e "\n${BLUE}Waiting for microservices to initialize...${NC}"
sleep 3

# Gateway (start last)
cd gateway
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
cd ..
echo -e "${GREEN}✓ Gateway started${NC} (port 8000)"

# Wait for Gateway to start
sleep 2

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ All services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📍 Service URLs:${NC}"
echo "   🔌 API Gateway:  http://localhost:8000"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   💚 Health Check: http://localhost:8000/health"
echo ""
echo -e "${BLUE}🔧 Microservice Endpoints:${NC}"
echo "   📍 Route:   http://localhost:8001"
echo "   🌤️  Weather: http://localhost:8002"
echo "   📌 POI:     http://localhost:8003"
echo "   🤖 AI:      http://localhost:8004"
echo ""
echo -e "${BLUE}🧪 Test System:${NC}"
echo "   ./test_api.sh"
echo ""
echo -e "${BLUE}🛑 Stop Services:${NC}"
echo "   ./stop.sh"
echo ""
