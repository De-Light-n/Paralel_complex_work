# UML-діаграма класів

## PlantUML код

Скопіюйте код нижче в [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/) або використайте VS Code з розширенням PlantUML.

```plantuml
@startuml Investment Portfolio Class Diagram

' Стилі
skinparam classAttributeIconSize 0
skinparam class {
    BackgroundColor<<Entity>> LightBlue
    BackgroundColor<<Service>> LightGreen
    BackgroundColor<<Repository>> LightYellow
    BackgroundColor<<Schema>> LightPink
    BorderColor Black
    ArrowColor Black
}

package "Asset Service" {
    class Asset <<Entity>> {
        - id: int
        - ticker: str
        - name: str
        - asset_type: AssetType
        - current_price: float
        - created_at: datetime
        - updated_at: datetime
        --
        + __repr__(): str
    }
    
    enum AssetType {
        STOCK
        CRYPTO
        BOND
        COMMODITY
    }
    
    class AssetRepository <<Repository>> {
        - session: AsyncSession
        --
        + create(asset_data): Asset
        + get_by_id(asset_id): Asset
        + get_by_ticker(ticker): Asset
        + get_all(skip, limit): List[Asset]
        + update(asset, data): Asset
        + delete(asset): void
    }
    
    class AssetService <<Service>> {
        - repository: AssetRepository
        - cache: CacheManager
        --
        + create_asset(data): AssetResponse
        + get_asset_by_id(id): AssetResponse
        + get_all_assets(skip, limit): dict
        + update_asset(id, data): AssetResponse
        + delete_asset(id): void
    }
    
    class AssetResponse <<Schema>> {
        + id: int
        + ticker: str
        + name: str
        + asset_type: AssetType
        + current_price: float
        + created_at: datetime
        + updated_at: datetime
    }
}

package "Portfolio Service" {
    class Investor <<Entity>> {
        - id: int
        - name: str
        - email: str
        - balance: float
        - created_at: datetime
        --
        + __repr__(): str
    }
    
    class PortfolioItem <<Entity>> {
        - id: int
        - investor_id: int
        - asset_id: int
        - quantity: float
        - average_buy_price: float
        - last_updated: datetime
        --
        + __repr__(): str
    }
    
    class PortfolioRepository <<Repository>> {
        - session: AsyncSession
        --
        + create_investor(data): Investor
        + get_investor_by_id(id): Investor
        + get_investor_by_email(email): Investor
        + get_portfolio_items(investor_id): List[PortfolioItem]
        + upsert_portfolio_item(...): PortfolioItem
    }
    
    class PortfolioService <<Service>> {
        - repository: PortfolioRepository
        --
        + create_investor(data): InvestorResponse
        + get_investor_by_id(id): InvestorResponse
        + get_portfolio(investor_id): PortfolioSummary
        + update_investor(id, data): InvestorResponse
    }
}

package "Transaction Service" {
    class Transaction <<Entity>> {
        - id: int
        - investor_id: int
        - asset_id: int
        - transaction_type: TransactionType
        - quantity: float
        - price_per_unit: float
        - total_amount: float
        - timestamp: datetime
        - notes: str
        --
        + __repr__(): str
    }
    
    enum TransactionType {
        BUY
        SELL
    }
    
    class TransactionRepository <<Repository>> {
        - session: AsyncSession
        --
        + create(data): Transaction
        + get_by_id(id): Transaction
        + get_all(skip, limit): List[Transaction]
        + get_by_investor(investor_id): List[Transaction]
        + get_investor_holdings(investor_id, asset_id): dict
    }
    
    class TransactionService <<Service>> {
        - repository: TransactionRepository
        --
        + create_transaction(data): TransactionResponse
        + get_transaction_by_id(id): TransactionResponse
        + get_all_transactions(skip, limit): dict
        + get_investor_transactions(investor_id): TransactionsByInvestorResponse
        - _validate_buy_transaction(data): void
        - _validate_sell_transaction(data): void
    }
}

package "Analytics Service" {
    class AnalyticsService <<Service>> {
        --
        + get_portfolio_analytics(investor_id): PortfolioAnalytics
        + get_risk_assessment(investor_id): RiskMetrics
        + get_transaction_summary(investor_id): TransactionSummary
        + generate_comprehensive_report(investor_id): ComprehensiveReport
        - _generate_recommendations(...): List[str]
    }
    
    class PortfolioAnalytics <<Schema>> {
        + investor_id: int
        + investor_name: str
        + total_balance: float
        + total_invested: float
        + current_portfolio_value: float
        + total_profit_loss: float
        + asset_allocation: List[AssetAllocation]
    }
    
    class RiskMetrics <<Schema>> {
        + investor_id: int
        + diversification_score: float
        + concentration_risk: str
        + largest_holding_percentage: float
        + risk_level: str
    }
}

package "Shared" {
    class CacheManager {
        - redis_client: Redis
        - default_ttl: int
        --
        + get(key): Any
        + set(key, value, ttl): bool
        + delete(key): bool
        + clear_pattern(pattern): int
    }
    
    class DatabaseManager {
        - engine: AsyncEngine
        - async_session_maker: async_sessionmaker
        --
        + create_tables(): void
        + get_session(): AsyncSession
        + close(): void
    }
    
    abstract class Base {
        <<SQLAlchemy Base>>
    }
}

' Зв'язки в межах Asset Service
Asset --> AssetType : has
AssetRepository --> Asset : manages
AssetService --> AssetRepository : uses
AssetService --> CacheManager : uses
AssetService ..> AssetResponse : creates

' Зв'язки в межах Portfolio Service
Investor "1" *-- "0..*" PortfolioItem : has
PortfolioRepository --> Investor : manages
PortfolioRepository --> PortfolioItem : manages
PortfolioService --> PortfolioRepository : uses

' Зв'язки в межах Transaction Service
Transaction --> TransactionType : has
TransactionRepository --> Transaction : manages
TransactionService --> TransactionRepository : uses

' Зв'язки Analytics Service
AnalyticsService ..> PortfolioAnalytics : creates
AnalyticsService ..> RiskMetrics : creates

' Міжсервісні зв'язки (HTTP)
TransactionService ..> AssetService : validates asset\n(HTTP)
TransactionService ..> PortfolioService : validates investor\n(HTTP)
PortfolioService ..> AssetService : gets prices\n(HTTP)
AnalyticsService ..> PortfolioService : fetches data\n(HTTP)
AnalyticsService ..> AssetService : fetches data\n(HTTP)
AnalyticsService ..> TransactionService : fetches data\n(HTTP)

' Успадкування від Base
Asset --|> Base
Investor --|> Base
PortfolioItem --|> Base
Transaction --|> Base

note right of AssetService
  Використовує Redis для
  кешування GET запитів
  (Lab #5 requirement)
end note

note right of AnalyticsService
  Безстанова служба
  Агрегує дані з інших сервісів
  Генерує звіти та рекомендації
end note

note bottom of TransactionService
  Валідує бізнес-логіку:
  - BUY: Перевіряє баланс
  - SELL: Перевіряє наявність активів
end note

@enduml
```

## Як використовувати

### Варіант 1: Online Editor
1. Відкрийте [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
2. Вставте код вище
3. Натисніть "Submit" або Ctrl+S
4. Збережіть діаграму як PNG або SVG

### Варіант 2: VS Code
1. Встановіть розширення "PlantUML" від jebbs
2. Створіть файл `class-diagram.puml`
3. Вставте код вище
4. Натисніть `Alt+D` для попереднього перегляду
5. Експортуйте в форматі: SVG, PNG, або PDF

### Варіант 3: Command Line (потрібен Java)
```bash
# Завантажте plantuml.jar
# Збережіть код у файл class-diagram.puml

java -jar plantuml.jar class-diagram.puml
```

## Опис діаграми

Діаграма показує:

1. **Asset Service**:
   - Entity: Asset з типом AssetType
   - Repository для доступу до даних
   - Service з бізнес-логікою та кешуванням
   - Schema для API відповідей

2. **Portfolio Service**:
   - Entity: Investor та PortfolioItem
   - Зв'язок один-до-багатьох між інвесторами та позиціями
   - Repository та Service шари

3. **Transaction Service**:
   - Entity: Transaction з типом TransactionType
   - Валідація бізнес-логіки (покупка/продаж)
   - Repository та Service шари

4. **Analytics Service**:
   - Безстанова служба
   - Агрегує дані з інших сервісів через HTTP
   - Генерує аналітику та рекомендації

5. **Shared Components**:
   - CacheManager для Redis
   - DatabaseManager для PostgreSQL
   - Base клас для всіх моделей

## Основні патерни

- **Layered Architecture**: Router → Service → Repository → Database
- **Repository Pattern**: Відокремлення логіки доступу до даних
- **Microservices Communication**: HTTP REST між сервісами
- **Caching Pattern**: Redis в Asset Service

## Для звіту

Ця діаграма демонструє:
- ✅ Структуру класів в кожному мікросервісі
- ✅ Layered Architecture (розділення відповідальності)
- ✅ Міжсервісну взаємодію
- ✅ Використання кешування (Lab #5)
- ✅ Repository Pattern
- ✅ REST принципи
