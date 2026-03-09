# Investment Portfolio Management System (Система управління інвестиційним портфелем)

## Architecture Overview
This project demonstrates the evolution from a monolithic application to a microservices architecture, as required for Laboratory Works #4, #5, and #6.

### Microservices
1. **Asset Service** - Manages investment assets (stocks, crypto) with Redis caching
2. **Transaction Service** - Handles buy/sell operations
3. **Portfolio Service** - Manages investors and their holdings
4. **Analytics Service** - Generates reports and calculates profitability

### Tech Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL (Async SQLAlchemy + asyncpg)
- **Caching:** Redis
- **Containerization:** Docker & Docker Compose
- **Orchestration:** Kubernetes

## Project Structure
```
├── asset-service/          # Asset management with Redis caching
├── transaction-service/    # Buy/Sell operations
├── portfolio-service/      # Investor and portfolio management
├── analytics-service/      # Reporting and analytics
├── shared/                 # Shared utilities and configs
├── docker/                 # Docker configuration
├── k8s/                    # Kubernetes manifests
└── docker-compose.yml      # Local development setup
```

## Running Locally with Docker Compose

```bash
docker-compose up --build
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Asset Service (port 8001)
- Transaction Service (port 8002)
- Portfolio Service (port 8003)
- Analytics Service (port 8004)

## API Endpoints

### Asset Service (http://localhost:8001)
- GET /assets - List all assets
- GET /assets/{id} - Get asset by ID (cached in Redis)
- POST /assets - Create new asset

### Transaction Service (http://localhost:8002)
- GET /transactions - List all transactions
- GET /transactions/{id} - Get transaction by ID
- POST /transactions - Create transaction (BUY/SELL)

### Portfolio Service (http://localhost:8003)
- GET /investors - List all investors
- GET /investors/{id} - Get investor by ID
- POST /investors - Create investor
- GET /portfolio/{investor_id} - Get portfolio holdings

### Analytics Service (http://localhost:8004)
- GET /analytics/portfolio/{investor_id} - Portfolio value and P/L
- GET /analytics/risk/{investor_id} - Risk assessment

## Kubernetes Deployment

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployments
kubectl get pods
kubectl get services
```

## Architecture Principles

### Layered Architecture
Each service follows a 3-layer architecture:
- **Router Layer** - HTTP endpoints (FastAPI routers)
- **Service Layer** - Business logic
- **Repository Layer** - Data access (SQLAlchemy)

### REST Principles
- Resource-based URLs
- HTTP methods (GET, POST, PUT, DELETE)
- Proper status codes (200, 201, 404, 500)
- JSON responses

### Microservices Communication
- HTTP/REST between services
- Each service has its own database
- Redis for caching (Asset Service)

## Laboratory Work Compliance

- **Lab #4:** Microservices architecture with service communication
- **Lab #5:** Docker containerization, Redis caching
- **Lab #6:** Kubernetes deployment with replicas and rolling updates
