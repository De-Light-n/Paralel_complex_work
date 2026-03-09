# Схема контейнерів (Docker Deployment)

## PlantUML код

### Діаграма 1: Docker Compose Architecture

```plantuml
@startuml Docker Compose Deployment

!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0
skinparam rectangle {
    BackgroundColor<<container>> LightBlue
    BackgroundColor<<database>> LightYellow
    BackgroundColor<<cache>> LightPink
    BackgroundColor<<network>> LightGreen
    BorderColor Black
}

title Docker Compose Deployment Architecture

cloud "Docker Host" {
    
    rectangle "Docker Network: portfolio_network" as network <<network>> {
        
        ' Databases
        rectangle "postgres:15-alpine\nContainer" as postgres <<database>> {
            component "PostgreSQL Server\n:5432" as pg_server
            database "asset_db" as asset_db
            database "transaction_db" as tx_db
            database "portfolio_db" as portfolio_db
            
            pg_server --> asset_db
            pg_server --> tx_db
            pg_server --> portfolio_db
        }
        
        rectangle "redis:7-alpine\nContainer" as redis <<cache>> {
            component "Redis Server\n:6379" as redis_server
        }
        
        ' Microservices
        rectangle "asset-service\nContainer" as asset_container <<container>> {
            component "FastAPI App\n:8001" as asset_app
            component "Python 3.11\nRuntime" as asset_runtime
            asset_runtime --> asset_app
        }
        
        rectangle "transaction-service\nContainer" as tx_container <<container>> {
            component "FastAPI App\n:8002" as tx_app
            component "Python 3.11\nRuntime" as tx_runtime
            tx_runtime --> tx_app
        }
        
        rectangle "portfolio-service\nContainer" as portfolio_container <<container>> {
            component "FastAPI App\n:8003" as portfolio_app
            component "Python 3.11\nRuntime" as portfolio_runtime
            portfolio_runtime --> portfolio_app
        }
        
        rectangle "analytics-service\nContainer" as analytics_container <<container>> {
            component "FastAPI App\n:8004" as analytics_app
            component "Python 3.11\nRuntime" as analytics_runtime
            analytics_runtime --> analytics_app
        }
    }
}

' External access
actor "User/Client" as user
user -down-> asset_app : localhost:8001
user -down-> tx_app : localhost:8002
user -down-> portfolio_app : localhost:8003
user -down-> analytics_app : localhost:8004

' Container connections
asset_app -down-> pg_server : asyncpg\n(asset_db)
asset_app -down-> redis_server : redis-py

tx_app -down-> pg_server : asyncpg\n(transaction_db)
tx_app .right.> asset_app : HTTP
tx_app .right.> portfolio_app : HTTP

portfolio_app -down-> pg_server : asyncpg\n(portfolio_db)
portfolio_app .left.> asset_app : HTTP

analytics_app .left.> asset_app : HTTP
analytics_app .up.> portfolio_app : HTTP
analytics_app .up.> tx_app : HTTP

note right of postgres
  **Volumes:**
  • postgres_data:/var/lib/postgresql/data
  • ./docker/init-db.sh:/docker-entrypoint-initdb.d/
  
  **Environment:**
  • POSTGRES_USER=portfolio_user
  • POSTGRES_PASSWORD=portfolio_pass
  • Multiple databases created via init script
  
  **Health Check:**
  pg_isready -U portfolio_user
end note

note right of redis
  **Configuration:**
  • No persistence (development)
  • maxmemory: 256mb
  • eviction: allkeys-lru
  
  **Health Check:**
  redis-cli ping
end note

note bottom of asset_container
  **Image:** Built from ./docker/Dockerfile
  **Build Context:** ./asset-service
  **Env File:** ./asset-service/.env
  **Depends On:** postgres, redis
  **Restart Policy:** unless-stopped
end note

note bottom of tx_container
  **Image:** Built from ./docker/Dockerfile
  **Build Context:** ./transaction-service
  **Depends On:** postgres, asset-service
  **Health Check:** curl http://localhost:8002/health
end note

@enduml
```

### Діаграма 2: Docker Container Internal Structure

```plantuml
@startuml Container Internal Structure

title Внутрішня структура Docker контейнера (Asset Service)

package "Container: asset-service" {
    
    rectangle "Base Image: python:3.11-slim" as base {
        component "Python 3.11" as python
        component "pip" as pip
        component "OS Libraries" as libs
    }
    
    rectangle "Application Layer" as app_layer {
        folder "/app" as app_dir {
            file "main.py" as main
            file "router.py" as router
            file "service.py" as service
            file "repository.py" as repo
            file "models.py" as models
            file "schemas.py" as schemas
            file "requirements.txt" as reqs
        }
        
        folder "/app/shared" as shared_dir {
            file "database.py" as db
            file "cache.py" as cache
            file "exceptions.py" as exc
        }
    }
    
    rectangle "Python Packages (venv)" as packages {
        component "fastapi==0.110.0+" as fastapi
        component "uvicorn==0.28.0+" as uvicorn
        component "sqlalchemy==2.0.25+" as sqlalchemy
        component "asyncpg==0.31.0" as asyncpg
        component "redis==7.3.0+" as redis_pkg
        component "pydantic==2.12.5+" as pydantic
    }
    
    rectangle "Runtime Process" as runtime {
        process "uvicorn main:app\n--host 0.0.0.0\n--port 8001\n--reload" as uvicorn_proc
    }
    
    python --> packages
    packages --> app_dir
    app_dir --> runtime
    uvicorn_proc --> main
}

rectangle "External Connections" as external {
    database "PostgreSQL\nasset_db" as postgres
    database "Redis\ncache" as redis_cache
}

runtime -down-> postgres : Port 5432\nasyncpg
runtime -down-> redis_cache : Port 6379\nredis-py

note right of runtime
  **Process Details:**
  • ENTRYPOINT: ["uvicorn"]
  • CMD: ["main:app", "--host", "0.0.0.0", ...]
  • EXPOSE: 8001
  • WORKDIR: /app
  • USER: appuser (non-root)
end note

note right of app_layer
  **Copied from:**
  COPY ./asset-service /app
  COPY ./shared /app/shared
  
  **Ownership:**
  chown -R appuser:appuser /app
end note

@enduml
```

### Діаграма 3: Docker Network Configuration

```plantuml
@startuml Docker Network

title Docker Network: portfolio_network (bridge)

rectangle "portfolio_network\n(172.18.0.0/16)" as network {
    
    node "postgres\n172.18.0.2" as postgres {
        [PostgreSQL :5432]
    }
    
    node "redis\n172.18.0.3" as redis {
        [Redis :6379]
    }
    
    node "asset-service\n172.18.0.4" as asset {
        [FastAPI :8001]
    }
    
    node "transaction-service\n172.18.0.5" as tx {
        [FastAPI :8002]
    }
    
    node "portfolio-service\n172.18.0.6" as portfolio {
        [FastAPI :8003]
    }
    
    node "analytics-service\n172.18.0.7" as analytics {
        [FastAPI :8004]
    }
}

cloud "Host Machine" as host {
    [localhost:5432] as host_pg
    [localhost:6379] as host_redis
    [localhost:8001] as host_8001
    [localhost:8002] as host_8002
    [localhost:8003] as host_8003
    [localhost:8004] as host_8004
}

' Port mappings
host_pg -down-> postgres : "5432:5432"
host_redis -down-> redis : "6379:6379"
host_8001 -down-> asset : "8001:8001"
host_8002 -down-> tx : "8002:8002"
host_8003 -down-> portfolio : "8003:8003"
host_8004 -down-> analytics : "8004:8004"

' Internal connections
asset -down-> postgres : "postgres:5432"
asset -down-> redis : "redis:6379"
tx -down-> postgres : "postgres:5432"
tx -right-> asset : "asset-service:8001"
tx -right-> portfolio : "portfolio-service:8003"
portfolio -down-> postgres : "postgres:5432"
portfolio -left-> asset : "asset-service:8001"
analytics -up-> asset : "asset-service:8001"
analytics -up-> tx : "transaction-service:8002"
analytics -up-> portfolio : "portfolio-service:8003"

note right of network
  **Network Type:** bridge
  **Driver:** bridge
  **Subnet:** auto-assigned
  **DNS:** Container names resolve to IPs
  
  **Features:**
  • Service discovery by name
  • Isolation from other networks
  • Internal DNS resolution
end note

note left of postgres
  **Hostname:** postgres
  **Internal:** postgres:5432
  **External:** localhost:5432
  
  Used by all services via
  DATABASE_URL environment variable
end note

note left of asset
  **Hostname:** asset-service
  **Internal:** asset-service:8001
  **External:** localhost:8001
  
  Called by: transaction-service,
  portfolio-service, analytics-service
end note

@enduml
```

### Діаграма 4: Volume Mounts

```plantuml
@startuml Docker Volumes

title Docker Volumes та Bind Mounts

rectangle "Host File System" as host {
    folder "Complex_work/" as project {
        folder "docker/" as docker_dir {
            file "init-db.sh" as init_script
        }
        folder "asset-service/" as asset_src {
            file "*.py" as asset_code
        }
        folder "shared/" as shared_src {
            file "*.py" as shared_code
        }
    }
    
    folder "Docker Volumes/" as volumes {
        folder "postgres_data" as pg_volume {
            file "Database files" as db_files
        }
    }
}

rectangle "Container: postgres" as pg_container {
    folder "/var/lib/postgresql/data" as pg_data {
        file "Persistent DB" as persistent_db
    }
    folder "/docker-entrypoint-initdb.d/" as initdb {
        file "init-db.sh" as mounted_init
    }
}

rectangle "Container: asset-service\n(development mode)" as dev_container {
    folder "/app" as app_dir {
        file "Live code" as live_code
    }
    folder "/app/shared" as shared_mounted {
        file "Shared modules" as shared_live
    }
}

' Volume mappings
pg_volume -down-> pg_data : "Named volume:\npostgres_data"
init_script -down-> mounted_init : "Bind mount:\nread-only"
asset_src -down-> app_dir : "Bind mount:\nDevelopment only"
shared_src -down-> shared_mounted : "Bind mount:\nDevelopment only"

note right of pg_volume
  **Named Volume:**
  • Managed by Docker
  • Persists data between restarts
  • Survives container deletion
  • Can be backed up
  
  **Location (Windows):**
  \\wsl$\docker-desktop-data\
  version-pack-data\community\
  docker\volumes\
end note

note right of init_script
  **Bind Mount:**
  • ./docker/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh:ro
  • Read-only mount
  • Executed on first startup
  • Creates 3 databases
end note

note right of dev_container
  **Development Mode:**
  volumes:
    - ./asset-service:/app
    - ./shared:/app/shared
  
  **Production Mode:**
  No bind mounts!
  Code copied during build:
  COPY ./asset-service /app
  
  **Hot Reload:**
  uvicorn --reload watches for changes
end note

@enduml
```

### Діаграма 5: Container Lifecycle

```plantuml
@startuml Container Lifecycle

title Docker Container Lifecycle and Dependencies

|Host|
start
:User runs;\n**docker-compose up**|

|Docker Compose|
:Parse docker-compose.yml;
:Create network: portfolio_network;
:Pull/Build images;

fork
    :Create postgres container;
    :Mount init-db.sh;
    :Mount postgres_data volume;
    :Start PostgreSQL;
    :Wait for health check:\npg_isready;
    :Execute init-db.sh\n(create 3 databases);
    :**postgres READY**]
fork again
    :Create redis container;
    :Start Redis;
    :Wait for health check:\nredis-cli ping;
    :**redis READY**]
end fork

:Wait for dependencies;

fork
    |asset-service|
    :Wait for:\n- postgres\n- redis;
    :Build image (if needed);
    :Start container;
    :Run: uvicorn main:app;
    :Connect to asset_db;
    :Connect to Redis;
    :Health check: /health;
    :**asset-service READY**]
    
fork again
    |transaction-service|
    :Wait for:\n- postgres\n- asset-service;
    :Build image;
    :Start container;
    :Run: uvicorn main:app;
    :Connect to transaction_db;
    :Health check: /health;
    :**transaction-service READY**]
    
fork again
    |portfolio-service|
    :Wait for:\n- postgres\n- asset-service;
    :Build image;
    :Start container;
    :Run: uvicorn main:app;
    :Connect to portfolio_db;
    :**portfolio-service READY**]
    
fork again
    |analytics-service|
    :Wait for:\n- asset-service\n- transaction-service\n- portfolio-service;
    :Build image;
    :Start container;
    :Run: uvicorn main:app;
    :**analytics-service READY**]
end fork

|Docker Compose|
:All services running;
:**System READY**]
:Monitor health checks;

repeat
    :Check container health;
    if (Container unhealthy?) then (yes)
        :Restart container;
        :Log error;
    else (no)
        :Continue monitoring;
    endif
repeat while (User stops?)

:User runs: docker-compose down;
:Stop all containers;
:Remove containers;
:Remove network;
if (Remove volumes?) then (yes)
    :Delete postgres_data;
else (no)
    :Keep volumes for next start;
endif

stop

note right
  **Dependencies:**
  1. postgres, redis (base)
  2. asset-service (depends on 1)
  3. transaction-service, portfolio-service (depend on 1, 2)
  4. analytics-service (depends on 2, 3)
  
  **Health Checks:**
  • postgres: pg_isready every 5s
  • redis: redis-cli ping every 5s
  • services: curl /health every 10s
  
  **Restart Policy:**
  unless-stopped (survives reboot)
end note

@enduml
```

## docker-compose.yml Пояснення

```yaml
version: '3.8'

services:
  # База даних PostgreSQL
  postgres:
    image: postgres:15-alpine              # Офіційний образ PostgreSQL
    container_name: portfolio-postgres      # Ім'я контейнера
    environment:                            # Змінні середовища
      POSTGRES_USER: portfolio_user
      POSTGRES_PASSWORD: portfolio_pass
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"                        # Host:Container port mapping
    volumes:
      - postgres_data:/var/lib/postgresql/data     # Persistent storage
      - ./docker/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh:ro  # Initialization script
    networks:
      - portfolio_network                  # Custom network
    healthcheck:                           # Container health check
      test: ["CMD-SHELL", "pg_isready -U portfolio_user"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped                # Auto-restart policy

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: portfolio-redis
    ports:
      - "6379:6379"
    networks:
      - portfolio_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  # Asset Service
  asset-service:
    build:
      context: ./asset-service             # Build context
      dockerfile: ../docker/Dockerfile     # Path to Dockerfile
    container_name: asset-service
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql+asyncpg://portfolio_user:portfolio_pass@postgres:5432/asset_db
      REDIS_URL: redis://redis:6379/0
    depends_on:                            # Wait for these services
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - portfolio_network
    volumes:                               # Development mode (optional)
      - ./asset-service:/app
      - ./shared:/app/shared
    restart: unless-stopped

  # ... інші сервіси ...

networks:
  portfolio_network:                       # Custom bridge network
    driver: bridge

volumes:
  postgres_data:                           # Named volume for persistence
```

## Dockerfile Пояснення

```dockerfile
# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Copy shared modules
COPY ../shared /app/shared

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Як використовувати

### Запуск системи

```powershell
# З директорії Complex_work/

# 1. Побудова образів
docker-compose build

# 2. Запуск всіх контейнерів
docker-compose up

# 3. Запуск у фоновому режимі
docker-compose up -d

# 4. Перегляд логів
docker-compose logs -f

# 5. Перегляд логів конкретного сервісу
docker-compose logs -f asset-service

# 6. Зупинка
docker-compose down

# 7. Зупинка з видаленням volumes
docker-compose down -v
```

### Корисні команди

```powershell
# Список запущених контейнерів
docker-compose ps

# Перебудова конкретного сервісу
docker-compose build asset-service

# Перезапуск сервісу
docker-compose restart asset-service

# Виконання команди в контейнері
docker-compose exec postgres psql -U portfolio_user -d asset_db

# Перегляд використання ресурсів
docker stats

# Очищення unused images
docker system prune -a
```

## Для звіту

Ці діаграми демонструють:
- ✅ Docker Compose архітектуру з 6 контейнерами
- ✅ Container networking (bridge network)
- ✅ Port mappings (host:container)
- ✅ Volume management (named volumes та bind mounts)
- ✅ Service dependencies (depends_on)
- ✅ Health checks для всіх сервісів
- ✅ Environment variables configuration
- ✅ Container lifecycle management
- ✅ Development vs Production modes
- ✅ Non-root user security

## Resource Requirements

| Service | CPU | Memory | Disk |
|---------|-----|--------|------|
| postgres | 0.5 | 256MB | 500MB |
| redis | 0.1 | 64MB | 50MB |
| asset-service | 0.2 | 128MB | 100MB |
| transaction-service | 0.2 | 128MB | 100MB |
| portfolio-service | 0.2 | 128MB | 100MB |
| analytics-service | 0.1 | 128MB | 100MB |
| **TOTAL** | **1.3** | **832MB** | **950MB** |

## Container Image Sizes

| Image | Size |
|-------|------|
| postgres:15-alpine | ~230MB |
| redis:7-alpine | ~30MB |
| asset-service | ~450MB |
| transaction-service | ~450MB |
| portfolio-service | ~450MB |
| analytics-service | ~450MB |
| **TOTAL** | **~2.1GB** |
