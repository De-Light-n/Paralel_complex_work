# 🎨 Додаткові діаграми (Draw.io / Визуальні інструменти)

Деякі діаграми краще робити візуальними інструментами, особливо якщо потрібна більша творча свобода або інфографічний стиль.

## 📊 Які діаграми краще робити візуально

### 1. Infrastructure Overview (Deployment Architecture)

**Інструмент:** Draw.io / diagrams.net

**Що показати:**
```
┌─────────────────────────────────────────────────────────┐
│                     INTERNET                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Load Balancer       │
         │   (Kubernetes Ingress)│
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Worker  │ │ Worker  │ │ Worker  │
    │ Node 1  │ │ Node 2  │ │ Node 3  │
    └────┬────┘ └────┬────┘ └────┬────┘
         │           │           │
         └───────────┴───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────┐           ┌─────────┐
    │PostgreSQL│           │  Redis  │
    │ Cluster │           │ Cluster │
    └─────────┘           └─────────┘
```

**Кроки в Draw.io:**
1. Відкрийте https://app.diagrams.net
2. Виберіть "Create New Diagram"
3. Шаблон: "Network" або "Cloud"
4. Додайте:
   - Хмару для Internet
   - Прямокутники для сервісів
   - Циліндри для баз даних
   - Стрілки для зв'язків
5. Використайте кольори:
   - Синій: Мережа
   - Зелений: Сервіси
   - Жовтий: Бази даних
   - Оранжевий: Cache

**Експорт:** File → Export as → PNG (300 DPI) або SVG

---

### 2. Data Flow Diagram (Потік даних)

**Інструмент:** Draw.io

**Приклад для BUY Transaction:**

```
[Користувач] 
    │
    │ 1. POST /transactions (BUY)
    ▼
[Transaction Service]
    │
    ├─ 2a. GET /assets/{id} ─────→ [Asset Service] ──→ [asset_db]
    │                               (validate)
    │
    ├─ 2b. GET /investors/{id} ──→ [Portfolio Service] ──→ [portfolio_db]
    │                               (check balance)
    │
    │ 3. INSERT transaction
    ▼
[transaction_db]
    │
    │ 4. UPDATE balance
    ▼
[Portfolio Service] ──→ [portfolio_db]
    │
    │ 5. INSERT/UPDATE holdings
    ▼
[portfolio_db]
    │
    │ 6. Response
    ▼
[Користувач]
```

**Кроки:**
1. Use "Flowchart" template
2. Додайте прямокутники для сервісів
3. Додайте циліндри для баз даних
4. Нумеруйте кроки
5. Використайте різні кольори для різних типів операцій:
   - Синій: HTTP calls
   - Зелений: Database operations
   - Червоний: Validation checks

---

### 3. Technology Stack Diagram

**Інструмент:** PowerPoint або Canva

**Структура:**

```
┌─────────────────────────────────────────────┐
│         USER INTERFACE LAYER                │
│  - Web Browser                              │
│  - Mobile App (future)                      │
│  - Postman / API Client                     │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────────┐
│         API GATEWAY (Optional)              │
│  - Kubernetes Ingress                       │
│  - NGINX / Traefik                          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│       MICROSERVICES LAYER                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Asset   │ │Transaction│ │Portfolio │   │
│  │ Service  │ │  Service  │ │ Service  │   │
│  └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐                              │
│  │Analytics │    Python 3.13 + FastAPI     │
│  │ Service  │    Uvicorn ASGI Server       │
│  └──────────┘                              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         DATA ACCESS LAYER                   │
│  - SQLAlchemy ORM (Async)                  │
│  - asyncpg Driver                          │
│  - Redis Client                            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         DATA STORAGE LAYER                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ asset_db │ │  tx_db   │ │portfolio │   │
│  │          │ │          │ │   _db    │   │
│  └──────────┘ └──────────┘ └──────────┘   │
│              PostgreSQL 15                  │
│                                             │
│  ┌──────────┐                              │
│  │  Redis   │  Cache (5 min TTL)           │
│  │  Cache   │                              │
│  └──────────┘                              │
└─────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      INFRASTRUCTURE LAYER                   │
│  - Docker (Development)                     │
│  - Kubernetes (Production)                  │
│  - Docker Compose (Orchestration)           │
└─────────────────────────────────────────────┘
```

**Кроки в PowerPoint:**
1. Створіть слайд з білим фоном
2. Додайте прямокутники для кожного шару
3. Використайте градієнт для зони мікросервісів
4. Додайте іконки (можна завантажити з flaticon.com):
   - 🌐 для User Interface
   - 🔄 для API Gateway
   - ⚙️ для Microservices
   - 💾 для Databases
   - 🐳 для Docker/Kubernetes
5. Експорт як PNG (високої якості)

**Альтернатива:** Canva (https://www.canva.com)
- Більше шаблонів
- Професійний вигляд
- Безкоштовний план доступний

---

### 4. Evolution Timeline (Монолітна → Мікросервісна)

**Інструмент:** PowerPoint / Google Slides

**Візуалізація:**

```
ЕТАП 1: Монолітна архітектура
┌────────────────────────────────┐
│                                │
│    MONOLITHIC APPLICATION      │
│                                │
│  ┌──────────────────────────┐ │
│  │   All Code in One Place  │ │
│  │   - Assets               │ │
│  │   - Transactions         │ │
│  │   - Portfolio            │ │
│  │   - Analytics            │ │
│  └──────────────────────────┘ │
│              │                 │
│              ▼                 │
│    ┌──────────────────┐       │
│    │  Single Database │       │
│    └──────────────────┘       │
└────────────────────────────────┘

        ⬇️ EVOLUTION ⬇️

ЕТАП 2: Мікросервісна архітектура
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Asset   │ │Transaction│ │Portfolio │ │Analytics │
│ Service  │ │  Service  │ │ Service  │ │ Service  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     ▼            ▼            ▼            │
┌─────────┐ ┌─────────┐ ┌─────────┐       │
│asset_db │ │  tx_db  │ │portfolio│       │ (stateless)
│         │ │         │ │  _db    │       │
└─────────┘ └─────────┘ └─────────┘       │
     │            │            │           │
     └────────────┴────────────┴───────────┘
              HTTP Communication
```

**Створення:**
1. Використайте два слайди (before/after) або один з анімацією
2. Додайте стрілку "Evolution" між ними
3. Підпишіть переваги/недоліки кожного підходу:

**Монолітна:**
- ✅ Простота
- ✅ Швидкий старт
- ❌ Важко масштабувати
- ❌ Один point of failure

**Мікросервісна:**
- ✅ Незалежне масштабування
- ✅ Fault isolation
- ❌ Складніша архітектура
- ❌ Network latency

---

### 5. Monitoring & Observability Stack (Додатково)

**Інструмент:** Draw.io

**Що показати:**

```
┌─────────────────────────────────────────────┐
│         APPLICATION LAYER                   │
│  [Asset] [Transaction] [Portfolio] [Analytics]
└──────────┬──────────────────────────────────┘
           │ Export metrics
           ▼
┌─────────────────────────────────────────────┐
│         MONITORING LAYER                    │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Prometheus│  │  Jaeger  │  │   ELK    │ │
│  │ (Metrics)│  │ (Tracing)│  │  (Logs)  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
└───────┼─────────────┼─────────────┼────────┘
        │             │             │
        └─────────────┴─────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │     Grafana      │
            │   (Dashboards)   │
            └──────────────────┘
                      │
                      ▼
                  [Admin User]
```

**Примітка:** Це advanced feature, не обов'язково для базової лабораторної, але дуже вражає в звіті!

---

### 6. Security Architecture (Додатково)

**Інструмент:** Draw.io

**Layers of Security:**

```
┌─────────────────────────────────────────────┐
│  NETWORK SECURITY                           │
│  - Firewall rules                           │
│  - VPC isolation (if cloud)                 │
│  - TLS/HTTPS encryption                     │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  APPLICATION SECURITY                       │
│  - Input validation (Pydantic)              │
│  - SQL injection prevention (ORM)           │
│  - CORS configuration                       │
│  - Rate limiting (optional)                 │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  DATA SECURITY                              │
│  - Encrypted at rest (PostgreSQL)           │
│  - Environment variables for secrets        │
│  - No hardcoded credentials                 │
│  - Kubernetes Secrets (production)          │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Інструменти та посилання

### Draw.io / diagrams.net
- **URL:** https://app.diagrams.net
- **Переваги:** Безкоштовний, online/offline, багато шаблонів
- **Шаблони для нашого проекту:**
  - Network Diagram
  - Cloud Architecture
  - Infrastructure
  - Flowchart

### Microsoft PowerPoint / Google Slides
- **Для:** Technology Stack, Evolution Timeline
- **Переваги:** Знайомий інтерфейс, легко додавати текст
- **Експорт:** Save as PNG (300+ DPI)

### Canva
- **URL:** https://www.canva.com
- **Для:** Інфографіка, красиві презентаційні діаграми
- **Переваги:** Професійні шаблони, легко використовувати
- **Ціна:** Безкоштовна версія достатня

### Lucidchart
- **URL:** https://www.lucidchart.com
- **Для:** Всі типи діаграм
- **Переваги:** Професійний інструмент, багато фігур
- **Ціна:** Безкоштовна trial версія

### Excalidraw
- **URL:** https://excalidraw.com
- **Для:** Швидкі hand-drawn діаграми
- **Стиль:** Схематичний, ескізний
- **Переваги:** Дуже швидко, виглядає uniq

---

## 📝 Checklist для візуальних діаграм

- [ ] Infrastructure Overview (де все розміщено)
- [ ] Data Flow для основних сценаріїв (BUY/SELL)
- [ ] Technology Stack (які технології використані)
- [ ] Evolution Timeline (від монолітної до мікросервісної)
- [ ] (Опціонально) Monitoring Stack
- [ ] (Опціонально) Security Layers

---

## 💡 Поради для гарних діаграм

1. **Консистентність кольорів:**
   - Виберіть палітру з 3-5 кольорів
   - Використайте один колір для одного типу компонентів
   - Рекомендована палітра:
     - #4A90E2 (Синій) - Сервіси
     - #F5A623 (Оранжевий) - Бази даних
     - #7ED321 (Зелений) - Успішні операції
     - #D0021B (Червоний) - Помилки/warning
     - #9013FE (Фіолетовий) - Cache/Redis

2. **Розмір шрифту:**
   - Заголовок: 18-24pt
   - Основний текст: 12-14pt
   - Підписи: 10-11pt
   - Експортуйте в високій роздільності (300 DPI)

3. **Whitespace (простір):**
   - Не переповнюйте діаграму
   - Залишайте простір між елементами
   - Групуйте пов'язані елементи

4. **Arrows (Стрілки):**
   - Тонкі лінії (1-2pt) для звичайних зв'язків
   - Товсті лінії (3-4pt) для важливих потоків
   - Пунктирні лінії для опціональних/async зв'язків
   - Підписуйте важливі стрілки

5. **Icons (Іконки):**
   - Використайте іконки для clarity
   - Джерела безкоштовних іконок:
     - https://www.flaticon.com
     - https://fontawesome.com
     - https://icons8.com
   - Розмір: 32x32 або 64x64 px

6. **Layers (Шари):**
   - Показуйте архітектуру в layers (User → API → Service → Data)
   - Від загального до детального (top-down)

---

## 🎓 Приклад опису для звіту

### Розділ: Інфраструктура системи

**Текст:**
> Система розгорнута в Kubernetes кластері з трьома worker nodes для забезпечення high availability.
> Kubernetes Ingress контролер виконує роль API Gateway та розподіляє навантаження між репліками сервісів.
> PostgreSQL та Redis розміщені в окремих StatefulSet для забезпечення persistent storage.
> Кожен мікросервіс має мінімум 2 репліки для fault tolerance, що дозволяє виконувати zero-downtime rolling updates.

**Діаграма:** [Вставте Infrastructure Overview з Draw.io]

**Підпис:**
> Рис. X. Kubernetes deployment architecture з high availability та load balancing

---

## 🚀 Швидкий старт

### Для базового звіту (мінімум):
1. Відкрийте https://app.diagrams.net
2. Створіть "Infrastructure Overview" (20 хвилин)
3. Створіть "Technology Stack" в PowerPoint (15 хвилин)
4. Експортуйте обидві в PNG
5. Готово! Маєте 2 додаткові діаграми

### Для просунутого звіту:
1. Всі діаграми з базового звіту
2. + Data Flow Diagram (30 хвилин)
3. + Evolution Timeline (20 хвилин)
4. + Monitoring Stack (якщо реалізовано) (20 хвилин)
5. Експортуйте в високій якості (SVG або 300 DPI PNG)

---

**Успіхів з створенням діаграм! Якщо PlantUML здається складним, візуальні інструменти - чудова альтернатива!** 🎨
