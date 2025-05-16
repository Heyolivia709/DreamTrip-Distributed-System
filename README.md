# Dream Trip - Distributed Intelligent Travel Planning System

A distributed travel planning system based on microservices architecture, providing route planning, weather forecasting, POI recommendations, and AI-powered intelligent summaries.

## 🎯 Key Features

-  **Microservices Architecture** - 5 independent microservices, independently deployable and scalable
-  **Event-Driven** - Kafka message queue for asynchronous processing
-  **API Gateway** - Unified entry point and service orchestration
-  **Distributed Cache** - Redis multi-level caching
-  **Fault Tolerance** - Service degradation and timeout control

## 🏗️ System Architecture

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │     (8000)      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │  Route  │         │ Weather │         │   POI   │
   │  (8001) │         │  (8002) │         │  (8003) │
   └─────────┘         └─────────┘         └─────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                        ┌────▼─────┐
                        │ AI Service│
                        │  (8004)   │
                        └───────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │PostgreSQL│        │  Redis  │         │  Kafka  │
   │  (5432) │         │  (6379) │         │  (9092) │
   └─────────┘         └─────────┘         └─────────┘
```

### Core Services

| Service | Port | Responsibility |
|---------|------|----------------|
| **API Gateway** | 8000 | Request routing, service orchestration, data aggregation |
| **Route Service** | 8001 | Route planning (Google Maps API) |
| **Weather Service** | 8002 | Weather forecast (OpenWeather API) |
| **POI Service** | 8003 | Point of interest recommendations (Google Places API) |
| **AI Service** | 8004 | Intelligent summary (Google Gemini API) |

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd dream_trip
```

### 2. Configure Environment Variables
```bash
cp env.example .env
# Edit .env file and add your API Keys (see Required API Keys section below)
```

### 3. Start Services
```bash
./start.sh
```

### 4. Access System
- **API Documentation**: http://204.236.144.38:8000/docs
- **Health Check**: http://204.236.144.38:8000/health

### 5. Test the System
```bash
# Run comprehensive API tests
./scripts/test_api.sh

# Test Kafka integration
./scripts/kafka_test.sh
```

## 🔑 Required API Keys

**⚠️ Important**: All services require valid API keys to function properly. Without API keys, services will fail.

Configure in `.env` file:
- `GOOGLE_MAPS_API_KEY` - Google Maps API (for route planning)
- `GOOGLE_PLACES_API_KEY` - Google Places API (for POI recommendations)
- `OPENWEATHER_API_KEY` - OpenWeather API (for weather forecasts)
- `GOOGLE_AI_API_KEY` - Google Gemini API (for AI summaries)

### How to Get API Keys:
1. **Google Maps/Places**: https://console.cloud.google.com/
2. **OpenWeather**: https://openweathermap.org/api
3. **Google Gemini**: https://makersuite.google.com/app/apikey

## 🛠️ Management Commands

```bash
# Start services
./start.sh

# Stop services
./stop.sh

# Test API
./scripts/test_api.sh

# Test Kafka
./scripts/kafka_test.sh

# Docker commands
docker-compose up -d    # Start
docker-compose down     # Stop
docker-compose logs -f  # View logs
```

## 📡 API Usage Examples

### Create Trip Plan
```bash
curl -X POST http://204.236.144.38:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "origin": "Beijing",
    "destination": "Shanghai",
    "preferences": ["food", "history"],
    "duration": 3
  }'
```

### Query Trip Details
```bash
curl http://204.236.144.38:8000/api/trip/1
```

## 🧪 Testing

- **Complete API Test**: `./scripts/test_api.sh` - Test all services and features
- **Kafka Integration Test**: `./scripts/kafka_test.sh` - Test event-driven functionality

## 🔧 Troubleshooting

### Common Issues:

1. **Services fail to start**
   ```bash
   # Check if ports are available
   docker-compose down
   ./start.sh
   ```

2. **API key errors**
   - Verify all API keys are correctly set in `.env` file
   - Check API key permissions and quotas
   - Restart services after updating API keys: `docker-compose restart`

3. **Database connection issues**
   ```bash
   # Reset database
   docker-compose down -v
   ./start.sh
   ```

4. **Check service logs**
   ```bash
   docker-compose logs -f [service_name]
   # e.g., docker-compose logs -f gateway
   ```

### Health Check:
```bash
curl http://204.236.144.38:8000/health
```
Should return: `{"status":"healthy","services":{"route":"healthy","weather":"healthy","poi":"healthy","ai":"healthy"}}`

