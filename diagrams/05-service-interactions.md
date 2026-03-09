# Взаємодія між сервісами (Sequence Diagrams)

## PlantUML код

### Діаграма 1: Купівля активу (BUY Transaction)

```plantuml
@startuml Buy Asset Transaction Flow

title Сценарій: Інвестор купує актив

actor "Інвестор" as investor
participant "Transaction\nService :8002" as tx_service
participant "Asset\nService :8001" as asset_service
participant "Portfolio\nService :8003" as portfolio_service
database "transaction_db" as tx_db
database "asset_db" as asset_db
database "portfolio_db" as portfolio_db

investor -> tx_service: POST /transactions\n{investor_id: 1, asset_id: 2,\ntype: "BUY", quantity: 10}
activate tx_service

tx_service -> tx_service: Validate request\n(Pydantic schema)

' Validate asset exists
tx_service -> asset_service: GET /assets/2
activate asset_service
asset_service -> asset_db: SELECT * FROM assets\nWHERE id = 2
activate asset_db
asset_db --> asset_service: Asset{id:2, ticker:"AAPL",\nprice: 180.5}
deactivate asset_db
asset_service --> tx_service: 200 OK\n{id:2, price: 180.5}
deactivate asset_service

' Validate investor and balance
tx_service -> portfolio_service: GET /investors/1
activate portfolio_service
portfolio_service -> portfolio_db: SELECT * FROM investors\nWHERE id = 1
activate portfolio_db
portfolio_db --> portfolio_service: Investor{id:1,\nbalance: 5000}
deactivate portfolio_db
portfolio_service --> tx_service: 200 OK\n{id:1, balance: 5000}
deactivate portfolio_service

tx_service -> tx_service: Calculate cost:\n10 * 180.5 = 1805\nCheck balance:\n5000 >= 1805 ✓

' Create transaction
tx_service -> tx_db: INSERT INTO transactions\n(investor_id, asset_id,\ntype, quantity, price,\ntotal: 1805)
activate tx_db
tx_db --> tx_service: Transaction created\n{id: 101}
deactivate tx_db

' Update investor balance
tx_service -> portfolio_service: PUT /investors/1\n{balance: 3195}
activate portfolio_service
portfolio_service -> portfolio_db: UPDATE investors\nSET balance = 3195\nWHERE id = 1
activate portfolio_db
portfolio_db --> portfolio_service: Updated
deactivate portfolio_db
portfolio_service --> tx_service: 200 OK
deactivate portfolio_service

' Update portfolio holdings
tx_service -> portfolio_service: POST /portfolio/update\n{investor_id: 1,\nasset_id: 2,\nquantity: +10,\navg_price: 180.5}
activate portfolio_service
portfolio_service -> portfolio_db: INSERT/UPDATE\nportfolio_items
activate portfolio_db
portfolio_db --> portfolio_service: Updated
deactivate portfolio_db
portfolio_service --> tx_service: 200 OK
deactivate portfolio_service

tx_service --> investor: 201 Created\n{id: 101,\ntotal_amount: 1805,\nstatus: "SUCCESS"}
deactivate tx_service

note right of tx_service
  **Валідація:**
  1. Asset exists
  2. Investor exists
  3. Balance sufficient
  4. Quantity > 0
  
  **Оновлення:**
  1. Create transaction
  2. Deduct balance
  3. Add to portfolio
end note

@enduml
```

### Діаграма 2: Продаж активу (SELL Transaction)

```plantuml
@startuml Sell Asset Transaction Flow

title Сценарій: Інвестор продає актив

actor "Інвестор" as investor
participant "Transaction\nService :8002" as tx_service
participant "Asset\nService :8001" as asset_service
participant "Portfolio\nService :8003" as portfolio_service
database "transaction_db" as tx_db
database "portfolio_db" as portfolio_db

investor -> tx_service: POST /transactions\n{investor_id: 1, asset_id: 2,\ntype: "SELL", quantity: 5}
activate tx_service

' Validate asset exists
tx_service -> asset_service: GET /assets/2
activate asset_service
asset_service --> tx_service: 200 OK\n{id:2, price: 185.0}
deactivate asset_service

' Check holdings
tx_service -> portfolio_service: GET /portfolio/1
activate portfolio_service
portfolio_service --> tx_service: 200 OK\nHoldings: {asset_id:2,\nquantity: 10}
deactivate portfolio_service

tx_service -> tx_service: Validate holdings:\n10 >= 5 ✓\nCalculate proceeds:\n5 * 185.0 = 925

' Create SELL transaction
tx_service -> tx_db: INSERT INTO transactions\n(type: "SELL",\nquantity: 5,\ntotal: 925)
activate tx_db
tx_db --> tx_service: Transaction created\n{id: 102}
deactivate tx_db

' Update balance (add proceeds)
tx_service -> portfolio_service: PUT /investors/1\n{balance: +925}
activate portfolio_service
portfolio_service --> tx_service: 200 OK
deactivate portfolio_service

' Update holdings (reduce quantity)
tx_service -> portfolio_service: POST /portfolio/update\n{investor_id: 1,\nasset_id: 2,\nquantity: -5}
activate portfolio_service
portfolio_service --> tx_service: 200 OK\nNew quantity: 5
deactivate portfolio_service

tx_service --> investor: 201 Created\n{id: 102,\ntotal_amount: 925,\nprofit: +120}
deactivate tx_service

note right of tx_service
  **Валідація SELL:**
  1. Asset exists
  2. Investor owns asset
  3. Quantity sufficient
  
  **Розрахунок прибутку:**
  avg_buy: 180.5
  sell_price: 185.0
  profit: (185-180.5)*5 = 22.5
end note

@enduml
```

### Діаграма 3: Генерація аналітичного звіту

```plantuml
@startuml Generate Analytics Report

title Сценарій: Генерація комплексного звіту про портфель

actor "Інвестор" as investor
participant "Analytics\nService :8004" as analytics
participant "Portfolio\nService :8003" as portfolio
participant "Asset\nService :8001" as asset
participant "Transaction\nService :8002" as tx
participant "Redis\nCache" as redis

investor -> analytics: GET /analytics/report/1
activate analytics

' Get investor info
analytics -> portfolio: GET /investors/1
activate portfolio
portfolio --> analytics: {id:1, name:"John",\nbalance: 3195}
deactivate portfolio

' Get portfolio holdings
analytics -> portfolio: GET /portfolio/1
activate portfolio
portfolio --> analytics: {holdings: [\n  {asset_id:2, qty:5, avg:180.5}\n]}
deactivate portfolio

' Get asset details (with cache)
loop For each asset in holdings
    analytics -> asset: GET /assets/2
    activate asset
    
    asset -> redis: GET "asset:2"
    activate redis
    
    alt Cache HIT
        redis --> asset: Cached data
        asset --> analytics: 200 OK (from cache)\n{id:2, price:185.0}
    else Cache MISS
        redis --> asset: null
        deactivate redis
        asset -> asset: Fetch from DB
        asset -> redis: SET "asset:2" (TTL 300s)
        activate redis
        redis --> asset: OK
        deactivate redis
        asset --> analytics: 200 OK (from DB)\n{id:2, price:185.0}
    end
    deactivate asset
end

' Get transaction history
analytics -> tx: GET /transactions?investor_id=1
activate tx
tx --> analytics: {transactions: [\n  {type:BUY, qty:10, price:180.5},\n  {type:SELL, qty:5, price:185.0}\n]}
deactivate tx

analytics -> analytics: Calculate metrics:\n- Total invested: 1805\n- Current value: 925\n- P&L: +22.5\n- Diversification: 1 asset\n- Risk level: HIGH

analytics -> analytics: Generate recommendations:\n- "Diversify portfolio"\n- "Consider bonds"

analytics --> investor: 200 OK\n{comprehensive_report}
deactivate analytics

note right of analytics
  **Агреговані дані:**
  • Інвестор: ім'я, баланс
  • Портфель: холдінги
  • Активи: поточні ціни
  • Транзакції: історія
  
  **Розраховані метрики:**
  • Total P&L
  • Diversification score
  • Risk assessment
  • Recommendations
end note

@enduml
```

### Діаграма 4: Кешування в Asset Service

```plantuml
@startuml Asset Service Caching

title Сценарій: Отримання інформації про актив з кешуванням

actor "Клієнт\n(інший сервіс)" as client
participant "Asset Service\nRouter" as router
participant "Asset Service\nLogic" as service
participant "Cache Manager" as cache
participant "Redis" as redis
participant "Repository" as repo
database "asset_db" as db

== Перший запит (Cache MISS) ==
client -> router: GET /assets/123
activate router
router -> service: get_asset_by_id(123)
activate service

service -> cache: get("asset:123")
activate cache
cache -> redis: GET "asset:123"
activate redis
redis --> cache: null (not found)
deactivate redis
cache --> service: None
deactivate cache

service -> service: Log: Cache MISS for asset:123

service -> repo: get_by_id(123)
activate repo
repo -> db: SELECT * FROM assets\nWHERE id = 123
activate db
db --> repo: Asset data
deactivate db
repo --> service: Asset object
deactivate repo

service -> cache: set("asset:123", data, ttl=300)
activate cache
cache -> redis: SET "asset:123" data EX 300
activate redis
redis --> cache: OK
deactivate redis
cache --> service: True
deactivate cache

service --> router: AssetResponse
deactivate service
router --> client: 200 OK\n{id:123, ticker:"BTC",\nprice: 45000}
deactivate router

== Другий запит через 10 секунд (Cache HIT) ==
client -> router: GET /assets/123
activate router
router -> service: get_asset_by_id(123)
activate service

service -> cache: get("asset:123")
activate cache
cache -> redis: GET "asset:123"
activate redis
redis --> cache: cached data
deactivate redis
cache --> service: Asset dict
deactivate cache

service -> service: Log: Cache HIT for asset:123

service --> router: AssetResponse (from cache)
deactivate service
router --> client: 200 OK\n{id:123, ticker:"BTC",\nprice: 45000}\n⚡ Fast response!
deactivate router

note right of service
  **Cache Strategy:**
  Cache-Aside pattern
  
  **TTL:** 300 seconds (5 min)
  
  **Key format:**
  "asset:{asset_id}"
  
  **Benefits:**
  • Reduced DB load
  • Faster response
  • < 50ms vs < 200ms
end note

note right of redis
  **Redis Configuration:**
  • Host: redis:6379
  • Default DB: 0
  • Eviction: allkeys-lru
  
  **Memory:**
  • Max: 256MB
  • Used: ~10MB
end note

@enduml
```

### Діаграма 5: Error Handling Flow

```plantuml
@startuml Error Handling

title Сценарій: Обробка помилок (недостатньо коштів)

actor "Інвестор" as investor
participant "Transaction\nService" as tx
participant "Portfolio\nService" as portfolio

investor -> tx: POST /transactions\n{investor_id: 1,\nasset_id: 2,\ntype: "BUY",\nquantity: 100}
activate tx

tx -> portfolio: GET /investors/1
activate portfolio
portfolio --> tx: 200 OK\n{balance: 1000}
deactivate portfolio

tx -> tx: Calculate cost:\n100 * 180 = 18000\nCheck balance:\n1000 < 18000 ✗

tx -> tx: raise InsufficientFundsException(\n  "Balance: 1000,\n   Required: 18000"\n)

tx --> investor: 400 Bad Request\n{\n  "error": "InsufficientFundsException",\n  "message": "Insufficient funds",\n  "details": {\n    "current_balance": 1000,\n    "required_amount": 18000,\n    "shortfall": 17000\n  }\n}
deactivate tx

note right of tx
  **Custom Exceptions:**
  • InsufficientFundsException (400)
  • ResourceNotFoundException (404)
  • BusinessLogicException (400)
  
  **Response Format:**
  {
    "error": "exception_type",
    "message": "human readable",
    "details": {...}
  }
end note

@enduml
```

## Як використовувати

1. Скопіюйте код в [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
2. Або використайте VS Code + PlantUML extension
3. Створіть окремі файли: `buy-flow.puml`, `sell-flow.puml`, тощо
4. Експортуйте кожну діаграму окремо

## Опис сценаріїв

### 📈 BUY Transaction Flow

**Кроки:**
1. Валідація запиту (Pydantic)
2. Перевірка існування активу (Asset Service)
3. Перевірка балансу інвестора (Portfolio Service)
4. Розрахунок вартості покупки
5. Створення транзакції (Transaction DB)
6. Списання коштів з балансу (Portfolio Service)
7. Додавання активу до портфеля (Portfolio Service)
8. Повернення результату

**Часова складність:** ~200-300ms (4 HTTP запити)

### 📉 SELL Transaction Flow

**Кроки:**
1. Валідація запиту
2. Перевірка існування активу
3. Перевірка наявності активу в портфелі
4. Перевірка достатньої кількості для продажу
5. Створення транзакції SELL
6. Додавання коштів до балансу
7. Зменшення кількості активу в портфелі
8. Повернення результату з розрахунком прибутку

**Часова складність:** ~200-300ms

### 📊 Analytics Report Flow

**Кроки:**
1. Отримання даних інвестора (Portfolio Service)
2. Отримання портфельних позицій (Portfolio Service)
3. Отримання поточних цін активів (Asset Service) - може використовувати кеш
4. Отримання історії транзакцій (Transaction Service)
5. Розрахунок метрик (P&L, diversification, risk)
6. Генерація рекомендацій
7. Формування звіту

**Часова складність:** ~500-800ms (багато HTTP запитів)

### ⚡ Caching Flow

**Cache HIT:**
- Asset Service перевіряє Redis
- Знаходить дані
- Повертає з кешу
- **Швидкість: ~20-50ms**

**Cache MISS:**
- Asset Service перевіряє Redis
- Не знаходить дані
- Запитує PostgreSQL
- Зберігає в Redis (TTL 300s)
- Повертає дані
- **Швидкість: ~150-200ms**

### ❌ Error Handling

**Типові помилки:**
- 400 Bad Request: недостатньо коштів, недостатньо активів
- 404 Not Found: актив не знайдено, інвестор не знайдено
- 422 Unprocessable Entity: invalid input (Pydantic validation)
- 500 Internal Server Error: database connection, unexpected errors

## Communication Patterns

### Synchronous REST (поточна реалізація)

**Переваги:**
- ✅ Простота реалізації
- ✅ Легко дебажити
- ✅ Request-Response гарантована відповідь

**Недоліки:**
- ❌ Висока затримка (latency)
- ❌ Cascading failures
- ❌ Tight coupling

### Asynchronous Messaging (можлива альтернатива)

```
Transaction Service
    ↓ (publish event)
Message Queue (RabbitMQ/Kafka)
    ↓ (subscribe)
Portfolio Service (updates portfolio)
```

**Переваги:**
- ✅ Loose coupling
- ✅ Better scalability
- ✅ Fault tolerance

**Недоліки:**
- ❌ Складніша реалізація
- ❌ Eventual consistency
- ❌ Harder to debug

## Performance Metrics

### Без кешування
- GET /assets/{id}: ~150-200ms
- POST /transactions: ~300-400ms
- GET /analytics/report: ~800-1200ms

### З кешуванням (Redis)
- GET /assets/{id} (cache hit): ~20-50ms ⚡
- GET /assets/{id} (cache miss): ~150-200ms
- POST /transactions: ~250-350ms (швидші валідації)
- GET /analytics/report: ~400-600ms (швидші запити до assets)

### Покращення продуктивності
- Cache Hit Rate: 70-80% для popular assets
- Response Time Reduction: 60-75% для cached requests
- Database Load Reduction: 70-80%

## Circuit Breaker Pattern (рекомендація для production)

```plantuml
@startuml Circuit Breaker

participant "Transaction\nService" as tx
participant "Circuit\nBreaker" as cb
participant "Asset\nService" as asset

tx -> cb: call Asset Service
activate cb

alt Circuit CLOSED (normal)
    cb -> asset: GET /assets/123
    activate asset
    asset --> cb: 200 OK
    deactivate asset
    cb --> tx: Success
    
else Circuit OPEN (too many failures)
    cb --> tx: 503 Service Unavailable\n(Fast fail)
    note right: No call to Asset Service
    
else Circuit HALF-OPEN (testing)
    cb -> asset: GET /assets/123 (test)
    activate asset
    alt Success
        asset --> cb: 200 OK
        deactivate asset
        cb -> cb: Close circuit
        cb --> tx: Success
    else Failure
        asset --> cb: Timeout
        deactivate asset
        cb -> cb: Open circuit again
        cb --> tx: 503 Service Unavailable
    end
end

deactivate cb

@enduml
```

## Для звіту

Ці діаграми демонструють:
- ✅ Послідовність викликів між мікросервісами
- ✅ Синхронну HTTP комунікацію
- ✅ Валідацію бізнес-логіки
- ✅ Кешування через Redis
- ✅ Обробку помилок
- ✅ Розподілені транзакції (2PC альтернатива)
- ✅ Performance optimization
- ✅ Resilience patterns (circuit breaker)

## Часова складність операцій

| Операція | HTTP Calls | Avg Time | Cache Impact |
|----------|-----------|----------|--------------|
| Create Asset | 0 | 50ms | N/A |
| Get Asset | 0 | 150ms | -70% with cache |
| Create Investor | 0 | 50ms | N/A |
| BUY Transaction | 2-3 | 300ms | -20% with asset cache |
| SELL Transaction | 2-3 | 300ms | -20% with asset cache |
| Get Portfolio | 1-5 | 400ms | -50% with asset cache |
| Analytics Report | 5-15 | 800ms | -50% with cache |
