#!/bin/bash

# Dream Trip stop script
# Usage: ./stop.sh

echo "🛑 Stopping Dream Trip services..."

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Stop all uvicorn processes
if ps aux | grep -E "uvicorn main:app" | grep -v grep > /dev/null; then
    echo -e "${YELLOW}Stopping all microservices...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null
    sleep 2
fi

# Check for remaining processes
if ps aux | grep -E "uvicorn main:app" | grep -v grep > /dev/null; then
    echo -e "${RED}Force stopping remaining processes...${NC}"
    pkill -9 -f "uvicorn main:app" 2>/dev/null
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All services stopped${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "💡 Tips:"
echo "   • Restart services: ./start.sh"
echo ""

