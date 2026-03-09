# Project Structure Overview
# Investment Portfolio Management System (Система управління інвестиційним портфелем)

```
Complex_work/
│
├── README.md                           # Main project documentation
├── API_TESTING_GUIDE.md               # Complete API testing guide
├── Task.md                             # Laboratory work requirements
├── docker-compose.yml                  # Docker orchestration
├── .dockerignore                       # Docker ignore file
│
├── shared/                             # Shared utilities and configurations
│   ├── __init__.py
│   ├── database.py                     # Async SQLAlchemy database manager
│   ├── cache.py                        # Redis cache manager
│   └── exceptions.py                   # Global exception handlers
│
├── asset-service/                      # Asset Service (with Redis caching)
│   ├── main.py                         # FastAPI application entry point
│   ├── models.py                       # SQLAlchemy models
│   ├── schemas.py                      # Pydantic schemas
│   ├── repository.py                   # Data access layer
│   ├── service.py                      # Business logic with caching
│   ├── router.py                       # API endpoints
│   └── requirements.txt                # Python dependencies
│
├── transaction-service/                # Transaction Service (Buy/Sell)
│   ├── main.py                         # FastAPI application entry point
│   ├── models.py                       # SQLAlchemy models
│   ├── schemas.py                      # Pydantic schemas
│   ├── repository.py                   # Data access layer
│   ├── service.py                      # Business logic
│   ├── router.py                       # API endpoints
│   └── requirements.txt                # Python dependencies
│
├── portfolio-service/                  # Portfolio Service (Investors)
│   ├── main.py                         # FastAPI application entry point
│   ├── models.py                       # SQLAlchemy models
│   ├── schemas.py                      # Pydantic schemas
│   ├── repository.py                   # Data access layer
│   ├── service.py                      # Business logic
│   ├── router.py                       # API endpoints
│   └── requirements.txt                # Python dependencies
│
├── analytics-service/                  # Analytics Service (Reports)
│   ├── main.py                         # FastAPI application entry point
│   ├── schemas.py                      # Pydantic schemas
│   ├── service.py                      # Business logic (aggregation)
│   ├── router.py                       # API endpoints
│   └── requirements.txt                # Python dependencies
│
├── docker/                             # Docker configuration
│   ├── Dockerfile                      # Generic Dockerfile for all services
│   └── init-db.sh                      # PostgreSQL initialization script
│
└── k8s/                                # Kubernetes manifests
    ├── README.md                       # Kubernetes deployment guide
    ├── postgres.yaml                   # PostgreSQL deployment & service
    ├── redis.yaml                      # Redis deployment & service
    ├── asset-service-configmap.yaml    # Asset Service configuration
    ├── asset-service-deployment.yaml   # Asset Service deployment
    ├── asset-service-service.yaml      # Asset Service service
    ├── transaction-service.yaml        # Transaction Service manifests
    ├── portfolio-service.yaml          # Portfolio Service manifests
    └── analytics-service.yaml          # Analytics Service manifests
```

## File Descriptions

### Root Level Files

- **README.md**: Main project documentation with architecture overview
- **API_TESTING_GUIDE.md**: Complete guide with curl/PowerShell examples
- **docker-compose.yml**: Orchestrates all services locally
- **.dockerignore**: Optimizes Docker builds

### Shared Module (`shared/`)

Common utilities used by all services:

- **database.py**: Async SQLAlchemy setup with session management
- **cache.py**: Redis cache manager with get/set/delete operations
- **exceptions.py**: Custom exceptions and global error handlers

### Asset Service (`asset-service/`)

Manages investment assets (stocks, crypto, etc.) with Redis caching.

**Key Features:**
- CRUD operations for assets
- Redis caching for GET operations (Lab #5 requirement)
- Layered architecture (Router → Service → Repository)

### Transaction Service (`transaction-service/`)

Handles buy/sell transactions with business logic validation.

**Key Features:**
- Create BUY/SELL transactions
- Validates investor balance (calls Portfolio Service)
- Validates asset existence (calls Asset Service)
- Inter-service HTTP communication

### Portfolio Service (`portfolio-service/`)

Manages investors and their portfolio holdings.

**Key Features:**
- Investor CRUD operations
- Portfolio tracking
- Calls Asset Service for current prices
- Calculates profit/loss

### Analytics Service (`analytics-service/`)

Stateless service that generates reports by aggregating data.

**Key Features:**
- Portfolio analytics
- Risk assessment
- Transaction summaries
- Comprehensive reports with recommendations
- Demonstrates microservices orchestration

### Docker (`docker/`)

- **Dockerfile**: Multi-stage build for Python services
- **init-db.sh**: Creates separate databases for each service

### Kubernetes (`k8s/`)

Complete Kubernetes deployment manifests:
- Deployments with 2 replicas (Lab #6 requirement)
- Rolling update strategy
- Health checks (liveness & readiness probes)
- Service discovery (ClusterIP services)
- ConfigMaps for configuration
- PersistentVolumeClaim for PostgreSQL

## Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI 0.109.0** - Modern async web framework
- **Pydantic 2.5.3** - Data validation
- **SQLAlchemy 2.0.25** - ORM with async support
- **asyncpg 0.29.0** - Async PostgreSQL driver

### Database & Cache
- **PostgreSQL 15** - Relational database
- **Redis 7** - In-memory cache

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local orchestration
- **Kubernetes** - Production orchestration

### HTTP Client
- **httpx 0.26.0** - Async HTTP client for inter-service communication

## Architecture Patterns

### 1. Microservices Architecture
Each service is independent with its own:
- Database (database-per-service pattern)
- Codebase
- Dependencies
- Deployment unit

### 2. Layered Architecture (within each service)
```
Router Layer     (HTTP endpoints, request/response handling)
    ↓
Service Layer    (Business logic, validation, orchestration)
    ↓
Repository Layer (Data access, database operations)
    ↓
Database Layer   (PostgreSQL)
```

### 3. Communication Patterns
- **Synchronous**: HTTP/REST for request-response
- **Service Discovery**: DNS-based (Kubernetes services)
- **Caching**: Redis for frequently accessed data

## Laboratory Work Compliance

### Lab #2: Basic REST API
✅ RESTful endpoints with proper HTTP methods
✅ Resource-based URLs
✅ JSON request/response
✅ Validation with Pydantic
✅ Error handling
✅ Correct HTTP status codes

### Lab #4: Microservices
✅ Service decomposition
✅ Inter-service communication (HTTP)
✅ Database per service
✅ Independent deployments

### Lab #5: Docker & Caching
✅ Docker containerization
✅ docker-compose orchestration
✅ Redis caching in Asset Service
✅ Multi-container setup

### Lab #6: Kubernetes
✅ Deployments with replicas (2 per service)
✅ Rolling update strategy
✅ Service discovery (ClusterIP)
✅ Health checks
✅ Resource limits
✅ Persistent storage (PostgreSQL)

## Running the Project

### Local Development (Docker Compose)

```bash
# Start all services
docker-compose up --build

# Access services:
# - Asset Service: http://localhost:8001
# - Transaction Service: http://localhost:8002
# - Portfolio Service: http://localhost:8003
# - Analytics Service: http://localhost:8004
```

### Kubernetes Deployment

```bash
# Build images
cd asset-service && docker build -t asset-service:latest -f ../docker/Dockerfile .
cd ../transaction-service && docker build -t transaction-service:latest -f ../docker/Dockerfile .
cd ../portfolio-service && docker build -t portfolio-service:latest -f ../docker/Dockerfile .
cd ../analytics-service && docker build -t analytics-service:latest -f ../docker/Dockerfile .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Verify deployment
kubectl get pods
kubectl get services
```

## Business Logic Implementation

### 1. Asset Management
- Create/Read/Update/Delete assets
- Price tracking
- Asset categorization (STOCK, CRYPTO, BOND, COMMODITY)

### 2. Transaction Processing
- Buy assets (validates funds)
- Sell assets (validates holdings)
- Transaction history
- Total amount calculation

### 3. Portfolio Management
- Investor accounts
- Balance tracking
- Holdings management
- Profit/loss calculation

### 4. Analytics & Reporting
- Portfolio value calculation
- Risk assessment
- Diversification analysis
- Investment recommendations

## API Endpoints Summary

### Asset Service (Port 8001)
- `GET /assets` - List all assets
- `POST /assets` - Create asset
- `GET /assets/{id}` - Get asset (cached)
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset

### Transaction Service (Port 8002)
- `GET /transactions` - List all transactions
- `POST /transactions` - Create transaction
- `GET /transactions/{id}` - Get transaction
- `GET /transactions/investor/{id}` - Investor's transactions

### Portfolio Service (Port 8003)
- `GET /investors` - List all investors
- `POST /investors` - Create investor
- `GET /investors/{id}` - Get investor
- `PUT /investors/{id}` - Update investor
- `GET /portfolio/{id}` - Get portfolio

### Analytics Service (Port 8004)
- `GET /analytics/portfolio/{id}` - Portfolio analytics
- `GET /analytics/risk/{id}` - Risk assessment
- `GET /analytics/transactions/{id}` - Transaction summary
- `GET /analytics/report/{id}` - Comprehensive report

## Security Considerations (for production)

- [ ] Add authentication (JWT tokens)
- [ ] Use secrets for database passwords
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add API gateway
- [ ] Use read-only database replicas
- [ ] Implement audit logging

## Future Enhancements

- [ ] Add message queue (RabbitMQ/Kafka) for async communication
- [ ] Implement CQRS pattern
- [ ] Add GraphQL API
- [ ] Implement event sourcing
- [ ] Add distributed tracing (Jaeger)
- [ ] Implement circuit breaker pattern
- [ ] Add API versioning
- [ ] Implement WebSocket for real-time updates
