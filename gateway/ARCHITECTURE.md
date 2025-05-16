# Gateway Modular Architecture Documentation
## 📁 Directory Structure

```
gateway/
├── main.py                    # Application entry (65 lines) - FastAPI app initialization
├── config.py                  # Configuration management - Environment variable loading
├── models.py                  # Database models - SQLAlchemy ORM
├── schemas.py                 # Request/Response models - Pydantic schemas
├── dependencies.py            # Dependency injection - Database, Redis connections
│
├── routers/                   # 🌐 Router Layer (HTTP interfaces)
│   ├── __init__.py
│   ├── health.py             # Health check routes
│   └── trip.py               # Trip planning routes
│
├── services/                  # 💼 Business Logic Layer
│   ├── __init__.py
│   ├── service_client.py     # Microservice client - Call other services
│   └── trip_service.py       # Trip planning business logic - Core business flow
│
└── repositories/              # 🗄️ Data Access Layer
    ├── __init__.py
    └── trip_repository.py    # Database operations - CRUD
```

---

## 🏗️ Architecture Design

### Three-Tier Architecture Pattern

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

## 📦 Module Responsibilities

### 1. **routers/** - Router Layer

#### `health.py` - Health Check
- `GET /` - Root path
- `GET /health` - Detailed health check (includes all microservice statuses)

#### `trip.py` - Trip Planning API
- `POST /api/trip/plan` - Create trip plan
- `GET /api/trip/{trip_id}` - Get trip plan details
- `GET /api/trips` - Get user trip list

**Responsibilities:**
- Receive HTTP requests
- Parameter validation (Pydantic)
- Dependency injection (Database, Redis)
- Call business logic layer
- Return responses

---

### 2. **services/** - Business Logic Layer

#### `service_client.py` - Microservice Client
```python
class ServiceClient:
    async def call_service(service_name, endpoint, data)
    async def check_service_health(service_name)
```

**Responsibilities:**
- Call other microservices (Route, Weather, POI, AI)
- Unified error handling
- Timeout control

#### `trip_service.py` - Trip Planning Business Logic
```python
class TripService:
    def create_trip_plan(request)              # Create trip plan
    async def process_trip_plan(trip_id, request)  # Background processing (call microservices)
    def get_trip_detail(trip_id)               # Get details (Redis → DB)
    def get_user_trips(user_id)                # Get list (DB → Redis)
```

**Responsibilities:**
- Core business logic
- Service orchestration (parallel calls to multiple microservices)
- Caching strategy (Redis priority, database fallback)
- Error handling and degradation

---

### 3. **repositories/** - Data Access Layer

#### `trip_repository.py` - Database Operations
```python
class TripRepository:
    @staticmethod
    def create_trip_plan(...)              # Create trip plan
    @staticmethod
    def update_trip_status(...)            # Update status
    @staticmethod
    def save_route(...)                    # Save route
    @staticmethod
    def save_weather_forecasts(...)        # Save weather
    @staticmethod
    def save_pois(...)                     # Save POIs
    @staticmethod
    def save_ai_summary(...)               # Save AI summary
    @staticmethod
    def get_trip_plan(...)                 # Query trip plan
    @staticmethod
    def get_user_trips(...)                # Query user list
```

**Responsibilities:**
- Encapsulate all database operations
- SQL queries
- Transaction management
- Error handling (return None/False when database unavailable)

---

## 🔄 Data Flow

### Create Trip Plan Flow

```
1. Frontend sends POST request
   ↓
2. routers/trip.py: create_trip_plan()
   - Validate request parameters
   - Inject dependencies (DB, Redis)
   ↓
3. services/trip_service.py: create_trip_plan()
   - Call repository to save to database
   - Get trip_id
   ↓
4. Add background task: process_trip_plan()
   - Call 4 microservices in parallel (Route, Weather, POI, AI)
   - Aggregate results
   - Save to Redis cache
   - Update database status
   ↓
5. Return response immediately: {trip_id, status: "processing"}
```

### Get Trip Plan Flow

```
1. Frontend sends GET request
   ↓
2. routers/trip.py: get_trip_plan()
   ↓
3. services/trip_service.py: get_trip_detail()
   - First get from Redis cache ✅
   - If not in cache, query from database
   - If not found anywhere, return None
   ↓
4. Return response or 404
```

---

## ✨ Modular Advantages

### 1. **Maintainability**
- Each module has single responsibility, easy to understand
- main.py reduced from 540 lines → 65 lines
- Modifying a feature only requires changing the corresponding module

### 2. **Testability**
- Each layer can be tested independently
- Easy to mock dependencies (database, Redis, microservices)
- Higher unit test coverage

### 3. **Extensibility**
- Adding new features only requires adding routers, services, repositories
- Does not affect existing code
- Follows Open-Closed Principle (open for extension, closed for modification)

### 4. **Code Reuse**
- `TripRepository` can be reused by multiple services
- `ServiceClient` uniformly manages microservice calls
- `dependencies.py` uniformly manages dependency injection

### 5. **Team Collaboration**
- Different developers can work on different layers simultaneously
- Reduces code conflicts
- Clear module boundaries

---

## 🔧 Dependency Injection

Using FastAPI's dependency injection system:

```python
# dependencies.py
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client

# routers/trip.py
@router.post("/api/trip/plan")
async def create_trip_plan(
    request: TripRequest,
    db: Session = Depends(get_db),        # Auto-inject
    redis_client = Depends(get_redis)     # Auto-inject
):
    trip_service = TripService(db, redis_client)
    ...
```

**Advantages:**
- Automatically manages resource lifecycle
- Easy to replace dependencies during testing
- Cleaner code

---

## 📝 Best Practices

### 1. **Router Layer**
- ✅ Only handle HTTP-related logic
- ✅ Use dependency injection
- ❌ Don't directly operate database
- ❌ Don't contain complex business logic

### 2. **Business Logic Layer**
- ✅ Contain core business logic
- ✅ Call data access layer
- ✅ Call external services
- ❌ Don't directly handle HTTP requests
- ❌ Don't directly write SQL

### 3. **Data Access Layer**
- ✅ Only responsible for database operations
- ✅ Encapsulate SQL queries
- ✅ Handle database exceptions
- ❌ Don't contain business logic
- ❌ Don't call external services

---

## 🚀 Running

```bash
# Start service
cd gateway
python3 main.py

# Or use uvicorn
uvicorn main:app --reload --port 8000
```

---
