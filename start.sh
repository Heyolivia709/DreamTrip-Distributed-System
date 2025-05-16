#!/bin/bash

# Dream Trip startup script
echo "🚀 Starting Dream Trip services..."

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Please run: cp env.example .env"
    echo "Then edit .env file and add your API Keys"
    exit 1
fi

# Start services
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Health check
echo "🔍 Checking service status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Services started successfully!"
    echo ""
    echo "📍 Access URLs:"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
    echo ""
    echo "🛑 Stop services: docker-compose down"
else
    echo "❌ Service startup failed"
    echo "Please check logs: docker-compose logs"
fi