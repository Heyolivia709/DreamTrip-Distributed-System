#!/bin/bash

# Dream Trip 停止脚本
# 使用方法: ./stop.sh

echo "🛑 停止 Dream Trip 服务..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 停止所有 uvicorn 进程
if ps aux | grep -E "uvicorn main:app" | grep -v grep > /dev/null; then
    echo -e "${YELLOW}停止所有微服务...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null
    sleep 2
fi

# 检查是否还有残留进程
if ps aux | grep -E "uvicorn main:app" | grep -v grep > /dev/null; then
    echo -e "${RED}强制停止残留进程...${NC}"
    pkill -9 -f "uvicorn main:app" 2>/dev/null
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 所有服务已停止${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "💡 提示："
echo "   • 重启服务: ./start.sh"
echo ""

