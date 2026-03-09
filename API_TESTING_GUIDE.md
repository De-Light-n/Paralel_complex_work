# API Testing Guide
# Investment Portfolio Management System

This guide provides example API requests for testing all microservices.
Use Postman, curl, or any HTTP client.

## Base URLs (Docker Compose)
- Asset Service: http://localhost:8001
- Transaction Service: http://localhost:8002
- Portfolio Service: http://localhost:8003
- Analytics Service: http://localhost:8004

---

## Asset Service

### 1. Create Assets

```bash
# Create Stock Asset (Apple)
curl -X POST http://localhost:8001/assets \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "asset_type": "STOCK",
    "current_price": 180.50
  }'

# Create Crypto Asset (Bitcoin)
curl -X POST http://localhost:8001/assets \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC",
    "name": "Bitcoin",
    "asset_type": "CRYPTO",
    "current_price": 45000.00
  }'

# Create Another Stock (Tesla)
curl -X POST http://localhost:8001/assets \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TSLA",
    "name": "Tesla Inc.",
    "asset_type": "STOCK",
    "current_price": 250.75
  }'
```

### 2. Get All Assets

```bash
curl http://localhost:8001/assets
```

### 3. Get Asset by ID (Demonstrates Redis Caching)

```bash
# First call: Fetches from database and caches in Redis
curl http://localhost:8001/assets/1

# Second call: Returns from Redis cache (faster!)
curl http://localhost:8001/assets/1
```

### 4. Update Asset Price

```bash
curl -X PUT http://localhost:8001/assets/1 \
  -H "Content-Type: application/json" \
  -d '{
    "current_price": 185.00
  }'
```

### 5. Error Handling - Get Non-Existent Asset

```bash
# Should return 404
curl http://localhost:8001/assets/999
```

---

## Portfolio Service

### 1. Create Investors

```bash
# Create First Investor
curl -X POST http://localhost:8003/investors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Іван Петренко",
    "email": "ivan.petrenko@example.com",
    "balance": 100000.00
  }'

# Create Second Investor
curl -X POST http://localhost:8003/investors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Марія Коваленко",
    "email": "maria.kovalenko@example.com",
    "balance": 50000.00
  }'
```

### 2. Get All Investors

```bash
curl http://localhost:8003/investors
```

### 3. Get Investor by ID

```bash
curl http://localhost:8003/investors/1
```

### 4. Update Investor Balance

```bash
curl -X PUT http://localhost:8003/investors/1 \
  -H "Content-Type: application/json" \
  -d '{
    "balance": 95000.00
  }'
```

### 5. Get Portfolio (Initially Empty)

```bash
curl http://localhost:8003/portfolio/1
```

### 6. Error Handling - Invalid Email

```bash
# Should return 422 validation error
curl -X POST http://localhost:8003/investors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "invalid-email",
    "balance": 10000.00
  }'
```

---

## Transaction Service

### 1. Buy Transactions

```bash
# Investor 1 buys 10 shares of AAPL
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 1,
    "asset_id": 1,
    "transaction_type": "BUY",
    "quantity": 10,
    "price_per_unit": 180.50,
    "notes": "Initial purchase of Apple stock"
  }'

# Investor 1 buys 0.5 BTC
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 1,
    "asset_id": 2,
    "transaction_type": "BUY",
    "quantity": 0.5,
    "price_per_unit": 45000.00,
    "notes": "Bitcoin investment"
  }'

# Investor 2 buys 5 shares of TSLA
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 2,
    "asset_id": 3,
    "transaction_type": "BUY",
    "quantity": 5,
    "price_per_unit": 250.75,
    "notes": "Tesla investment"
  }'
```

### 2. Sell Transaction

```bash
# Investor 1 sells 3 shares of AAPL
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 1,
    "asset_id": 1,
    "transaction_type": "SELL",
    "quantity": 3,
    "price_per_unit": 185.00,
    "notes": "Taking some profit"
  }'
```

### 3. Get All Transactions

```bash
curl http://localhost:8002/transactions
```

### 4. Get Transaction by ID

```bash
curl http://localhost:8002/transactions/1
```

### 5. Get Investor's Transactions

```bash
curl http://localhost:8002/transactions/investor/1
```

### 6. Error Handling - Insufficient Funds

```bash
# Try to buy more than balance allows
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 2,
    "asset_id": 1,
    "transaction_type": "BUY",
    "quantity": 1000,
    "price_per_unit": 180.50,
    "notes": "This should fail"
  }'
```

### 7. Error Handling - Selling More Than Owned

```bash
# Try to sell more shares than owned
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 1,
    "asset_id": 1,
    "transaction_type": "SELL",
    "quantity": 100,
    "price_per_unit": 185.00,
    "notes": "This should fail"
  }'
```

---

## Analytics Service

### 1. Get Portfolio Analytics

```bash
# Get detailed portfolio analytics for Investor 1
curl http://localhost:8004/analytics/portfolio/1
```

**Expected Response:**
- Total invested amount
- Current portfolio value
- Profit/Loss calculations
- Asset allocation breakdown
- Percentage distribution

### 2. Get Risk Assessment

```bash
# Get risk metrics for Investor 1
curl http://localhost:8004/analytics/risk/1
```

**Expected Response:**
- Diversification score
- Concentration risk level
- Largest holding percentage
- Overall risk level (CONSERVATIVE/MODERATE/AGGRESSIVE)

### 3. Get Transaction Summary

```bash
# Get transaction statistics for Investor 1
curl http://localhost:8004/analytics/transactions/1
```

**Expected Response:**
- Total number of transactions
- Buy vs Sell breakdown
- Total invested and received amounts
- Net cash flow
- Average transaction size

### 4. Generate Comprehensive Report

```bash
# Generate full investment report for Investor 1
curl http://localhost:8004/analytics/report/1
```

**Expected Response:**
- Complete portfolio analytics
- Risk assessment
- Transaction summary
- Personalized investment recommendations

---

## Testing Scenarios for Lab Report

### Scenario 1: Complete Investment Journey

```bash
# 1. Create an investor
curl -X POST http://localhost:8003/investors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Олександр Шевченко",
    "email": "oleksandr@example.com",
    "balance": 200000.00
  }'

# 2. Create some assets
curl -X POST http://localhost:8001/assets \
  -H "Content-Type: application/json" \
  -d '{"ticker": "GOOGL", "name": "Alphabet Inc.", "asset_type": "STOCK", "current_price": 140.00}'

# 3. Buy assets
curl -X POST http://localhost:8002/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": 3,
    "asset_id": 4,
    "transaction_type": "BUY",
    "quantity": 100,
    "price_per_unit": 140.00,
    "notes": "Initial Google investment"
  }'

# 4. Check portfolio
curl http://localhost:8003/portfolio/3

# 5. Get analytics
curl http://localhost:8004/analytics/report/3
```

### Scenario 2: Testing Cache Performance

```bash
# First request (DB query)
time curl http://localhost:8001/assets/1

# Second request (Redis cache - should be faster)
time curl http://localhost:8001/assets/1

# Check logs to see "Cache HIT" vs "Cache MISS"
docker logs asset_service
```

### Scenario 3: Microservices Communication

```bash
# Analytics service demonstrates microservices orchestration
# It calls:
# - Portfolio Service → to get holdings
# - Asset Service → to get current prices
# - Transaction Service → to get transaction history

curl http://localhost:8004/analytics/report/1

# Check logs to see inter-service HTTP calls
docker logs analytics_service
```

---

## Health Checks

```bash
# Check all services are healthy
curl http://localhost:8001/health  # Asset Service
curl http://localhost:8002/health  # Transaction Service
curl http://localhost:8003/health  # Portfolio Service
curl http://localhost:8004/health  # Analytics Service
```

---

## Windows PowerShell Examples

```powershell
# Create investor
Invoke-RestMethod -Uri "http://localhost:8003/investors" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"Test User","email":"test@example.com","balance":10000.00}'

# Get all assets
Invoke-RestMethod -Uri "http://localhost:8001/assets" -Method GET

# Create transaction
Invoke-RestMethod -Uri "http://localhost:8002/transactions" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"investor_id":1,"asset_id":1,"transaction_type":"BUY","quantity":10,"price_per_unit":180.50}'

# Get analytics report
Invoke-RestMethod -Uri "http://localhost:8004/analytics/report/1" -Method GET
```

---

## Expected HTTP Status Codes

- **200 OK**: Successful GET, PUT requests
- **201 Created**: Successful POST (resource created)
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Business logic error (insufficient funds, etc.)
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Unexpected error

---

## Notes for Laboratory Report

### REST Principles Demonstrated:
✅ Resource-based URLs (/assets, /investors, /transactions)
✅ HTTP methods (GET, POST, PUT, DELETE)
✅ JSON request/response format
✅ Proper HTTP status codes
✅ Stateless communication

### Microservices Architecture:
✅ Service independence
✅ HTTP-based communication
✅ Database per service
✅ Service discovery via DNS

### Lab #5 - Docker & Caching:
✅ Redis caching in Asset Service
✅ Docker containerization
✅ docker-compose orchestration

### Lab #6 - Kubernetes:
✅ Deployments with replicas
✅ Rolling updates
✅ Service discovery
✅ Health checks
