# Gateway Service - Dream Trip

API Gateway for the Distributed Travel Planning System - **Modular Architecture**

---

## 🚀 Quick Start

### Start Service
```bash
cd gateway
python3 main.py
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Create trip plan
curl -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Shanghai",
    "destination": "Hangzhou",
    "preferences": ["nature", "history"],
    "duration": 2
  }'

# Get trip details
curl http://localhost:8000/api/trip/{trip_id}

# Get trip list
curl http://localhost:8000/api/trips
```

---

## 📁 Project Structure

```
gateway/
├── main.py                    # Application entry point (65 lines)
├── config.py                  # Configuration management
├── models.py                  # Database models
├── schemas.py                 # Request/Response models
├── dependencies.py            # Dependency injection
│
├── routers/                   # Router layer
│   ├── health.py             # GET / and /health
│   └── trip.py               # Travel planning routes
│
├── services/                  # Business logic layer
│   ├── service_client.py     # Microservice client
│   ├── trip_service.py       # Trip planning business logic
│   └── kafka_producer.py     # Kafka event producer
│
└── repositories/              # Data access layer
    └── trip_repository.py    # Database operations
```

---

## 🏗️ Architecture

### Three-Tier Architecture

```
┌──────────────────────────────────────────────┐
│  Routers (Router Layer)                      │
│  - Handle HTTP requests                      │
│  - Parameter validation                      │
│  - Dependency injection                      │
└────────────────┬─────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────┐
│  Services (Business Logic Layer)             │
│  - Core business logic                       │
│  - Service orchestration                     │
│  - Transaction management                    │
└────────────────┬─────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────┐
│  Repositories (Data Access Layer)            │
│  - Database CRUD operations                  │
│  - Data persistence                          │
│  - Query encapsulation                       │
└──────────────────────────────────────────────┘
```

---

## 🔑 Key Features

### 1. Service Orchestration
- Calls 4 microservices in parallel (Route, Weather, POI, AI)
- Aggregates results
- Asynchronous processing using background tasks

### 2. Distributed Cache
- Redis priority (Cache-Aside pattern)
- Database fallback
- 80%+ cache hit rate

### 3. Event-Driven
- Publishes events via Kafka
- Decouples event producers and consumers
- Supports multiple event subscribers

### 4. Modular Design
- Three-tier architecture (Router → Service → Repository)
- Clear separation of concerns
- Easy to test and maintain

---

## 📊 Key Endpoints

### Health Check

**GET /** or **GET /health**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T10:30:00",
  "services": {
    "route": "healthy",
    "weather": "healthy",
    "poi": "healthy",
    "ai": "healthy"
  }
}
```

### Create Trip Plan

**POST /api/trip/plan**

Request:
```json
{
  "user_id": 1,
  "origin": "Shanghai",
  "destination": "Hangzhou",
  "preferences": ["nature", "history"],
  "duration": 2
}
```

Response:
```json
{
  "trip_id": 1234567890,
  "status": "processing"
}
```

### Query Trip Details

**GET /api/trip/{trip_id}**

Response:
```json
{
  "trip_id": 1234567890,
  "status": "completed",
  "route": {...},
  "weather": [...],
  "pois": [...],
  "ai_summary": {...}
}
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dream_trip

# Redis
REDIS_URL=redis://localhost:6379

# Kafka
KAFKA_BROKER=localhost:9092

# Microservices
ROUTE_SERVICE_URL=http://localhost:8001
WEATHER_SERVICE_URL=http://localhost:8002
POI_SERVICE_URL=http://localhost:8003
AI_SERVICE_URL=http://localhost:8004
```

---

## 📚 Documentation

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md)

---

**Built with FastAPI and Python**
