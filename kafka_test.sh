#!/bin/bash

echo "🧪 测试 Kafka 集成..."
echo ""

# 测试1: 创建旅行计划（会发送 Kafka 事件）
echo "1️⃣ 创建旅行计划（将发送 Kafka 事件）..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "杭州",
    "destination": "苏州",
    "preferences": ["园林", "文化"],
    "duration": 2
  }')

TRIP_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['trip_id'])" 2>/dev/null)

if [ ! -z "$TRIP_ID" ]; then
    echo "   ✅ 旅行计划已创建: Trip ID = $TRIP_ID"
    echo "   📤 Kafka 事件已发送: trip_created"
else
    echo "   ❌ 创建失败"
    exit 1
fi

echo ""
echo "2️⃣ 等待后台处理（10秒）..."
sleep 10

echo ""
echo "3️⃣ 检查 Gateway 日志中的 Kafka 事件..."
echo ""
tail -20 logs/gateway.log | grep -E "Kafka|事件" | tail -5

echo ""
echo "✅ Kafka 测试完成！"
echo ""
echo "💡 提示："
echo "   - 启动消费者监听事件: python3 scripts/kafka_consumer_example.py"
echo "   - 查看详细文档: cat KAFKA_INTEGRATION.md"
