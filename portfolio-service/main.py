"""
Portfolio Service - Main Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import DatabaseManager
from shared.exceptions import register_exception_handlers
from router import router

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_db"
)

db_manager = DatabaseManager(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    print("Starting Portfolio Service...")
    await db_manager.create_tables()
    print("Database connected")
    yield
    print("Shutting down Portfolio Service...")
    await db_manager.close()


app = FastAPI(
    title="Portfolio Service",
    description="Investment Portfolio Management - Portfolio Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


async def get_db_session():
    """Provide database session"""
    async for session in db_manager.get_session():
        yield session


from router import get_portfolio_service
from service import PortfolioService
from repository import PortfolioRepository


async def get_portfolio_service_override(db=Depends(get_db_session)):
    """Override for portfolio service dependency"""
    repository = PortfolioRepository(db)
    return PortfolioService(repository)


app.dependency_overrides[get_portfolio_service] = get_portfolio_service_override

app.include_router(router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Portfolio Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
