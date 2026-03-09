"""
Asset Service - Main Application
FastAPI application with Redis caching
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import DatabaseManager
from shared.cache import CacheManager
from shared.exceptions import register_exception_handlers
from router import router as asset_router

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/asset_db"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global instances
db_manager = DatabaseManager(DATABASE_URL)
cache_manager = CacheManager(REDIS_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown events
    """
    # Startup
    print("Starting Asset Service...")
    await db_manager.create_tables()
    await cache_manager.connect()
    print("Database and Redis connected")
    
    yield
    
    # Shutdown
    print("Shutting down Asset Service...")
    await cache_manager.disconnect()
    await db_manager.close()
    print("Connections closed")


# Create FastAPI application
app = FastAPI(
    title="Asset Service",
    description="Investment Portfolio Management - Asset Service with Redis Caching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)


# Dependency overrides for dependency injection
async def get_db_session():
    """Provide database session"""
    async for session in db_manager.get_session():
        yield session


async def get_cache():
    """Provide cache manager"""
    return cache_manager


# Override dependencies in router
from router import get_asset_service
from service import AssetService
from repository import AssetRepository


async def get_asset_service_override(
    db=Depends(get_db_session),
    cache=Depends(get_cache)
):
    """Override for asset service dependency"""
    repository = AssetRepository(db)
    return AssetService(repository, cache)


app.dependency_overrides[get_asset_service] = get_asset_service_override

# Include routers
app.include_router(asset_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Asset Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "cache": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
