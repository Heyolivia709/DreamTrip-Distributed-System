# Gateway Service - API Gateway & Service Orchestration

## 🎯 Overview

The Gateway service acts as the central entry point for the Dream Trip distributed system, providing API routing, service orchestration, and data aggregation.

## 🏗️ Architecture

```
Client Request → Gateway (8000) → Microservices
                     ↓
                [Route, Weather, POI, AI Services]
                     ↓
                [PostgreSQL, Redis, Kafka]
```

## 📁 Project Structure

### Core Services
- **API Gateway** (8000) - Request routing and service orchestration
- **Route Service** (8001) - Route planning via Google Maps API
- **Weather Service** (8002) - Weather forecasts via OpenWeather API
- **POI Service** (8003) - Point of interest recommendations
- **AI Service** (8004) - Intelligent trip summaries via Gemini API

### Infrastructure
- **PostgreSQL** (5432) - Primary database
- **Redis** (6379) - Distributed caching
- **Kafka** (9092) - Event-driven messaging

## 🗂️ Gateway Code Structure

### `/routers/` - API Endpoints
- `trip.py` - Trip planning endpoints
- `health.py` - Health check endpoints

### `/services/` - Business Logic
- `trip_service.py` - Main coordinator 
- `trip_plan_service.py` - Trip plan CRUD & caching
- `trip_processing_service.py` - Background processing
- `service_client.py` - Microservice communication
- `kafka_producer.py` - Event messaging

### `/repositories/` - Data Access
- `base_repository.py` - Common database operations
- `trip_repository.py` - Trip plan data access
- `route_repository.py` - Route data access
- `weather_repository.py` - Weather data access
- `poi_repository.py` - POI data access
- `ai_repository.py` - AI summary data access

## 🔄 Request Flow

1. **Client Request** → Gateway API endpoint
2. **Trip Creation** → `trip_service.py` coordinates
3. **Plan Management** → `trip_plan_service.py` handles CRUD
4. **Background Processing** → `trip_processing_service.py` orchestrates
5. **Microservice Calls** → `service_client.py` communicates
6. **Event Publishing** → `kafka_producer.py` sends events
7. **Data Persistence** → Repository layer saves to database

## 🚀 Key Features

- **Service Orchestration** - Coordinates multiple microservices
- **Event-Driven Architecture** - Kafka for asynchronous processing
- **Distributed Caching** - Redis for performance optimization
- **Fault Tolerance** - Graceful degradation when services fail
- **Modular Design** - Clean separation of concerns

## 📡 API Endpoints

- `POST /api/trip/plan` - Create trip plan
- `GET /api/trip/{trip_id}` - Get trip details
- `GET /api/trips` - Get user trip list
- `GET /health` - Health check

## 🛠️ Development

```bash
# Start services
docker-compose up -d

# Run tests
./scripts/test_api.sh

# View logs
docker-compose logs -f gateway
```

## 🔧 Configuration

Configure API keys in `.env`:
- `GOOGLE_MAPS_API_KEY`
- `GOOGLE_PLACES_API_KEY`
- `OPENWEATHER_API_KEY`
- `GEMINI_API_KEY`