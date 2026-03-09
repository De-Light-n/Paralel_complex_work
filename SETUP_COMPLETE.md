# 🚀 Quick Reference - Investment Portfolio Management System

## ✅ Installation Complete!

All Python packages are successfully installed:
- FastAPI 0.135.1
- Uvicorn 0.41.0
- Pydantic 2.12.5
- SQLAlchemy 2.0.48
- asyncpg 0.31.0
- Redis 7.3.0
- HTTPX 0.28.1
- And all other dependencies

---

## 🎯 How to Run

### Option 1: Docker Compose (EASIEST - Recommended)

```powershell
# Start all services (Postgres, Redis, and 4 microservices)
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Services will be available at:**
- Asset Service: http://localhost:8001
- Transaction Service: http://localhost:8002
- Portfolio Service: http://localhost:8003
- Analytics Service: http://localhost:8004

**API Documentation:**
- http://localhost:8001/docs
- http://localhost:8002/docs
- http://localhost:8003/docs
- http://localhost:8004/docs

---

### Option 2: Run Locally (for Development)

**Prerequisites:**
1. Install and start PostgreSQL
2. Install and start Redis

**Create databases in PostgreSQL:**
```sql
CREATE DATABASE asset_db;
CREATE DATABASE transaction_db;
CREATE DATABASE portfolio_db;
```

**Run each service in a separate terminal:**

**Terminal 1 - Asset Service:**
```powershell
cd asset-service
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/asset_db"
$env:REDIS_URL="redis://localhost:6379/0"
python main.py
```

**Terminal 2 - Transaction Service:**
```powershell
cd transaction-service
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/transaction_db"
$env:ASSET_SERVICE_URL="http://localhost:8001"
$env:PORTFOLIO_SERVICE_URL="http://localhost:8003"
python main.py
```

**Terminal 3 - Portfolio Service:**
```powershell
cd portfolio-service
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db"
$env:ASSET_SERVICE_URL="http://localhost:8001"
python main.py
```

**Terminal 4 - Analytics Service:**
```powershell
cd analytics-service
.\.venv\Scripts\Activate.ps1
$env:ASSET_SERVICE_URL="http://localhost:8001"
$env:PORTFOLIO_SERVICE_URL="http://localhost:8003"
$env:TRANSACTION_SERVICE_URL="http://localhost:8002"
python main.py
```

---

## 🧪 Quick Test

**1. Create an asset:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/assets" `
  -Method POST -ContentType "application/json" `
  -Body '{"ticker":"AAPL","name":"Apple Inc.","asset_type":"STOCK","current_price":180.50}'
```

**2. Create an investor:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8003/investors" `
  -Method POST -ContentType "application/json" `
  -Body '{"name":"Іван Петренко","email":"ivan@example.com","balance":100000.00}'
```

**3. Buy some stock:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8002/transactions" `
  -Method POST -ContentType "application/json" `
  -Body '{"investor_id":1,"asset_id":1,"transaction_type":"BUY","quantity":10,"price_per_unit":180.50}'
```

**4. Get portfolio:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8003/portfolio/1"
```

**5. Get analytics report:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8004/analytics/report/1"
```

---

## 📚 Documentation Files

- **[README.md](README.md)** - Main project overview
- **[QUICK_START.md](QUICK_START.md)** - Detailed setup guide  
- **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)** - Complete API examples
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Architecture details
- **[k8s/README.md](k8s/README.md)** - Kubernetes deployment guide

---

## 🐳 Docker Commands

```powershell
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f asset-service

# Stop services
docker-compose down

# Clean everything
docker-compose down -v
docker system prune -a
```

---

## ☸️ Kubernetes Deployment

```powershell
# Build images
docker build -t asset-service:latest -f docker/Dockerfile ./asset-service
docker build -t transaction-service:latest -f docker/Dockerfile ./transaction-service
docker build -t portfolio-service:latest -f docker/Dockerfile ./portfolio-service
docker build -t analytics-service:latest -f docker/Dockerfile ./analytics-service

# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services

# Port forward
kubectl port-forward service/asset-service 8001:8000
kubectl port-forward service/transaction-service 8002:8000
kubectl port-forward service/portfolio-service 8003:8000
kubectl port-forward service/analytics-service 8004:8000
```

---

## 🔍 Troubleshooting

**Port already in use:**
```powershell
# Find process
netstat -ano | findstr :8001

# Kill process
taskkill /PID <PID> /F
```

**Docker issues:**
```powershell
# Restart Docker Desktop
# Then rebuild:
docker-compose down -v
docker-compose up --build
```

**Database connection issues:**
- Check PostgreSQL is running
- Verify credentials: `postgres:postgres`
- Check database names: `asset_db`, `transaction_db`, `portfolio_db`

---

## ✅ Lab Requirements Checklist

### Lab #2 - REST API
- [x] RESTful endpoints
- [x] HTTP methods (GET, POST, PUT, DELETE)
- [x] JSON request/response
- [x] Pydantic validation
- [x] Error handling
- [x] Correct status codes

### Lab #4 - Microservices
- [x] 4 independent services
- [x] HTTP communication between services
- [x] Database per service
- [x] Service orchestration

### Lab #5 - Docker & Caching
- [x] Docker containerization
- [x] docker-compose setup
- [x] Redis caching (Asset Service)
- [x] Multi-container orchestration

### Lab #6 - Kubernetes
- [x] Deployments with 2 replicas
- [x] Rolling update strategy
- [x] ClusterIP services
- [x] Health checks
- [x] ConfigMaps
- [x] Persistent storage

---

## 📝 For Your Report

**Key Screenshots:**
1. Docker Compose running (all 6 containers)
2. API Documentation pages (/docs)
3. Postman/curl requests & responses
4. Kubernetes pods (`kubectl get pods`)
5. Redis cache logs (HIT vs MISS)
6. Error handling examples

**Code to Highlight:**
1. Layered architecture (router → service → repository)
2. Redis caching in Asset Service
3. Inter-service communication
4. Pydantic validation
5. Exception handling

---

## 🎉 You're All Set!

The system is ready to run. Start with Docker Compose for the easiest experience:

```powershell
docker-compose up --build
```

Then visit http://localhost:8001/docs to explore the API!

Good luck with your laboratory work! 🎓
