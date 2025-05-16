#!/bin/bash

echo "🧪 Testing Kafka integration..."
echo ""

# Test 1: Create trip plan (will send Kafka event)
echo "1️⃣ Creating trip plan (will send Kafka event)..."
RESPONSE=$(curl -s -X POST http://204.236.144.38:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Hangzhou",
    "destination": "Suzhou",
    "preferences": ["gardens", "culture"],
    "duration": 2
  }')

TRIP_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['trip_id'])" 2>/dev/null)

if [ ! -z "$TRIP_ID" ]; then
    echo "   ✅ Trip plan created: Trip ID = $TRIP_ID"
    echo "   📤 Kafka event sent: trip_created"
else
    echo "   ❌ Creation failed"
    exit 1
fi

echo ""
echo "2️⃣ Waiting for background processing (10 seconds)..."
sleep 10

echo ""
echo "3️⃣ Checking Kafka events in Gateway logs..."
echo ""
tail -20 logs/gateway.log | grep -E "Kafka|event" | tail -5

echo ""
echo "✅ Kafka test completed!"
echo ""
echo "💡 Tips:"
echo "   - Start consumer to listen for events: python3 scripts/kafka_consumer_example.py"
echo "   - View detailed documentation: cat KAFKA_INTEGRATION.md"
