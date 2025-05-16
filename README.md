# Dream Trip - Distributed Intelligent Travel Planning System

> A distributed travel planning system based on microservices architecture, showcasing modern distributed system design patterns and best practices

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-green.svg)](https://fastapi.tiangolo.com/)
[![Kafka](https://img.shields.io/badge/Kafka-Event%20Driven-orange.svg)](https://kafka.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Key Features

- 🏗️ **Microservices Architecture** - 5 independent microservices, independently deployable and scalable
- 🔄 **Event-Driven** - Kafka message queue for asynchronous processing
- 🚀 **API Gateway** - Unified entry point and service orchestration
- 💾 **Distributed Cache** - Redis multi-level caching with 80%+ hit rate
- 🛡️ **Fault Tolerance** - Service degradation, circuit breaker, and timeout control

---

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

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Redis

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dream_trip
```

### 2. Configure Environment Variables

```bash
cp env.example .env
# Edit .env and fill in your API Keys
```

### 3. Start Infrastructure Services

```bash
# Start PostgreSQL, Kafka, Zookeeper
docker-compose up -d postgres kafka zookeeper

# Start Redis (if not installed)
brew install redis
brew services start redis
```

### 4. Start Microservices

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r gateway/requirements.txt

# Start all services
./start.sh
```

### 5. Access Services

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Swagger UI**: Test all endpoints in API documentation

---

## 📡 API Usage Examples

### Create Trip Plan

```bash
curl -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "origin": "Beijing",
    "destination": "Shanghai",
    "preferences": ["food", "history"],
    "duration": 3
  }'
```

**Response**:
```json
{
  "trip_id": 1234567890,
  "status": "processing"
}
```

### Query Trip Details

```bash
curl http://localhost:8000/api/trip/1234567890
```

**Response**:
```json
{
  "trip_id": 1234567890,
  "status": "completed",
  "route": { "distance": "1,213 km", "duration": "11 hours" },
  "weather": [...],
  "pois": [...],
  "ai_summary": {...}
}
```

---

## 🔧 Tech Stack

### Backend Framework
- **FastAPI** - High-performance async web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

### Data Storage
- **PostgreSQL** - Relational database
- **Redis** - Distributed cache
- **Kafka** - Message queue

### External APIs
- Google Maps API
- Google Places API
- OpenWeather API
- Google Gemini API

---

## 📊 Project Structure

```
dream_trip/
├── gateway/                    # API Gateway (modular architecture)
│   ├── routers/               # Router layer
│   ├── services/              # Business logic layer
│   └── repositories/          # Data access layer
│
├── route_service/             # Route planning service
├── weather_service/           # Weather forecast service
├── poi_service/               # POI recommendation service
├── ai_summary_service/        # AI summary service
│
├── docs/                      # Detailed documentation
│   └── USAGE_GUIDE.md        # Usage guide
│
├── docker-compose.yml         # Docker orchestration
├── start.sh                   # Startup script
├── stop.sh                    # Stop script
└── test_api.sh               # API testing script
```

---

## 🧪 Testing

### Run Complete Tests

```bash
./test_api.sh
```

### Test Coverage
- ✅ Health check (all services)
- ✅ Create trip plan
- ✅ Query trip details
- ✅ Direct microservice calls
- ✅ 11 tests, 100% pass rate

---

## 📊 Service Management

### Start Services

```bash
./start.sh
```

### Stop Services

```bash
./stop.sh
```

### Check Service Status

```bash
# View running services
ps aux | grep "python3 -m uvicorn"

# Health check
curl http://localhost:8000/health
```

---

## 📚 Detailed Documentation

- 📘 [Usage Guide](docs/USAGE_GUIDE.md) - Detailed features, testing guide, distributed features demo
- 📗 [Gateway Architecture](gateway/ARCHITECTURE.md) - Modular architecture details
- 📙 [Environment Configuration](env.example) - Environment variable configuration examples

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

## 📄 License

MIT License

---

## 🌟 Star History

If this project helps you, please give it a Star ⭐️

---

**Built with ❤️ using FastAPI, Kafka, and Python**
