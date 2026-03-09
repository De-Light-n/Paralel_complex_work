# Quick Start Guide
# Investment Portfolio Management System

## Prerequisites

- **Python 3.11+** installed
- **Docker Desktop** installed and running
- **Git** (optional, for version control)
- **Postman** or **curl** for API testing

## 🚀 Quick Start with Docker Compose (Recommended)

### Step 1: Start All Services

```powershell
# Navigate to project directory
cd "c:\Унік\курс 3.2\Паралельні обчислення і розподілені системи\Complex_work"

# Start all services
docker-compose up --build
```

Wait for all services to start (you'll see logs from all containers).

### Step 2: Verify Services are Running

```powershell
# Check Asset Service
Invoke-RestMethod -Uri "http://localhost:8001/health"

# Check Transaction Service
Invoke-RestMethod -Uri "http://localhost:8002/health"

# Check Portfolio Service  
Invoke-RestMethod -Uri "http://localhost:8003/health"

# Check Analytics Service
Invoke-RestMethod -Uri "http://localhost:8004/health"
```

All should return `{"status": "healthy"}` or similar.

### Step 3: Create Test Data

```powershell
# Create an asset (Apple stock)
Invoke-RestMethod -Uri "http://localhost:8001/assets" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"ticker":"AAPL","name":"Apple Inc.","asset_type":"STOCK","current_price":180.50}'

# Create an investor
Invoke-RestMethod -Uri "http://localhost:8003/investors" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"Іван Петренко","email":"ivan@example.com","balance":100000.00}'

# Create a buy transaction
Invoke-RestMethod -Uri "http://localhost:8002/transactions" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"investor_id":1,"asset_id":1,"transaction_type":"BUY","quantity":10,"price_per_unit":180.50}'

# Get portfolio analytics
Invoke-RestMethod -Uri "http://localhost:8004/analytics/report/1"
```

### Step 4: Access API Documentation

Open in your browser:
- Asset Service: http://localhost:8001/docs
- Transaction Service: http://localhost:8002/docs
- Portfolio Service: http://localhost:8003/docs
- Analytics Service: http://localhost:8004/docs

### Step 5: Stop Services

```powershell
# Stop all services (Ctrl+C in the terminal, then:)
docker-compose down

# Or to remove volumes as well:
docker-compose down -v
```

---

## 🐍 Running Locally Without Docker

### Step 1: Install Dependencies

```powershell
# Install PostgreSQL 15
# Download from: https://www.postgresql.org/download/windows/

# Install Redis
# Download from: https://github.com/microsoftarchive/redis/releases

# Create databases
psql -U postgres
CREATE DATABASE asset_db;
CREATE DATABASE transaction_db;
CREATE DATABASE portfolio_db;
\q
```

### Step 2: Set Up Virtual Environments

```powershell
# Asset Service
cd asset-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..

# Repeat for other services...
```

### Step 3: Start Services

```powershell
# Terminal 1 - Asset Service
cd asset-service
.\venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/asset_db"
$env:REDIS_URL="redis://localhost:6379/0"
python main.py

# Terminal 2 - Transaction Service
cd transaction-service
.\venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/transaction_db"
python main.py

# Terminal 3 - Portfolio Service
cd portfolio-service
.\venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db"
python main.py

# Terminal 4 - Analytics Service
cd analytics-service
.\venv\Scripts\Activate.ps1
python main.py
```

---

## ☸️ Kubernetes Deployment

### Step 1: Build Docker Images

```powershell
# Build Asset Service
cd asset-service
docker build -t asset-service:latest -f ..\docker\Dockerfile .

# Build Transaction Service
cd ..\transaction-service
docker build -t transaction-service:latest -f ..\docker\Dockerfile .

# Build Portfolio Service
cd ..\portfolio-service
docker build -t portfolio-service:latest -f ..\docker\Dockerfile .

# Build Analytics Service
cd ..\analytics-service
docker build -t analytics-service:latest -f ..\docker\Dockerfile .

cd ..
```

### Step 2: Deploy to Kubernetes

```powershell
# Apply all manifests
kubectl apply -f k8s\

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all --timeout=300s

# Check status
kubectl get pods
kubectl get services
```

### Step 3: Access Services (Port Forwarding)

```powershell
# In separate terminals:
kubectl port-forward service/asset-service 8001:8000
kubectl port-forward service/transaction-service 8002:8000
kubectl port-forward service/portfolio-service 8003:8000
kubectl port-forward service/analytics-service 8004:8000
```

---

## 📝 Testing the System

### Complete Test Scenario

```powershell
# 1. Create assets
$assets = @(
    @{ticker="AAPL"; name="Apple Inc."; asset_type="STOCK"; current_price=180.50},
    @{ticker="BTC"; name="Bitcoin"; asset_type="CRYPTO"; current_price=45000.00},
    @{ticker="TSLA"; name="Tesla Inc."; asset_type="STOCK"; current_price=250.75}
)

foreach ($asset in $assets) {
    Invoke-RestMethod -Uri "http://localhost:8001/assets" `
        -Method POST `
        -ContentType "application/json" `
        -Body ($asset | ConvertTo-Json)
}

# 2. Create investor
$investor = @{
    name = "Олександр Шевченко"
    email = "oleksandr@example.com"
    balance = 200000.00
}

Invoke-RestMethod -Uri "http://localhost:8003/investors" `
    -Method POST `
    -ContentType "application/json" `
    -Body ($investor | ConvertTo-Json)

# 3. Buy assets
$transactions = @(
    @{investor_id=1; asset_id=1; transaction_type="BUY"; quantity=10; price_per_unit=180.50},
    @{investor_id=1; asset_id=2; transaction_type="BUY"; quantity=0.5; price_per_unit=45000.00},
    @{investor_id=1; asset_id=3; transaction_type="BUY"; quantity=5; price_per_unit=250.75}
)

foreach ($tx in $transactions) {
    Invoke-RestMethod -Uri "http://localhost:8002/transactions" `
        -Method POST `
        -ContentType "application/json" `
        -Body ($tx | ConvertTo-Json)
}

# 4. Get portfolio
Invoke-RestMethod -Uri "http://localhost:8003/portfolio/1"

# 5. Get comprehensive report
Invoke-RestMethod -Uri "http://localhost:8004/analytics/report/1"

# 6. Test Redis caching (Asset Service)
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8001/assets/1" }  # First call (DB)
Measure-Command { Invoke-RestMethod -Uri "http://localhost:8001/assets/1" }  # Second call (Cache - faster!)
```

---

## 🔍 Troubleshooting

### Docker Compose Issues

```powershell
# Check logs
docker-compose logs asset-service
docker-compose logs postgres
docker-compose logs redis

# Restart specific service
docker-compose restart asset-service

# Clean start
docker-compose down -v
docker-compose up --build
```

### Kubernetes Issues

```powershell
# Check pod status
kubectl get pods

# View logs
kubectl logs -l app=asset-service

# Describe pod for details
kubectl describe pod <pod-name>

# Delete and recreate
kubectl delete -f k8s\
kubectl apply -f k8s\
```

### Common Issues

**Issue: Port already in use**
```powershell
# Find process using port
netstat -ano | findstr :8001

# Kill process
taskkill /PID <PID> /F
```

**Issue: Database connection failed**
- Ensure PostgreSQL is running
- Check DATABASE_URL environment variable
- Verify credentials

**Issue: Redis connection failed**
- Ensure Redis is running
- Check REDIS_URL environment variable
- Try: `redis-cli ping` (should return PONG)

---

## 📊 Viewing Application Logs

### Docker Compose

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f asset-service

# Last 100 lines
docker-compose logs --tail=100 asset-service
```

### Kubernetes

```powershell
# All pods with label
kubectl logs -l app=asset-service -f

# Specific pod
kubectl logs <pod-name> -f

# Previous container (if crashed)
kubectl logs <pod-name> --previous
```

---

## 🎯 Next Steps

1. ✅ Read [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) for complete API examples
2. ✅ Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details
3. ✅ Check [k8s/README.md](k8s/README.md) for Kubernetes deployment guide
4. ✅ Explore API docs at http://localhost:8001/docs (and other ports)

---

## 📚 For Laboratory Report

### Screenshots to Include:

1. **Docker Compose** running all services
2. **API Documentation** (FastAPI /docs pages)
3. **Postman/curl** requests and responses
4. **Docker logs** showing cache HIT/MISS
5. **Kubernetes pods** and services (kubectl get all)
6. **Error handling** examples (404, 400, 422)

### Code to Highlight:

1. **Layered Architecture** (router → service → repository)
2. **Redis Caching** (service.py in Asset Service)
3. **Inter-service Communication** (service.py in Transaction/Analytics)
4. **Pydantic Validation** (schemas.py)
5. **Exception Handling** (shared/exceptions.py)

### Testing Scenarios:

1. Create → Read → Update → Delete (CRUD)
2. Cache performance (first vs second GET)
3. Business logic validation (insufficient funds)
4. Microservices orchestration (Analytics calling other services)
5. Error handling (invalid data, non-existent resources)

---

## 💡 Tips

- Use **Postman Collections** to save and organize requests
- Enable **Docker Desktop Kubernetes** for easy local testing
- Use **VS Code** with Docker and Kubernetes extensions
- Check **health endpoints** before running tests
- Monitor **logs** to understand service communication
- Use **API documentation** (/docs) for exploring endpoints

---

## 🆘 Need Help?

- Check logs first: `docker-compose logs -f`
- Verify services are healthy: `curl http://localhost:8001/health`
- Review error messages in API responses
- Ensure all dependencies are installed
- Check environment variables are set correctly

Good luck with your laboratory work! 🎓
