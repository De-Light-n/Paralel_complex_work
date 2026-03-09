"""
Transaction Service - Main Application
FastAPI application for transaction management
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import DatabaseManager
from shared.exceptions import register_exception_handlers
from router import router as transaction_router

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/transaction_db"
)

# Global instances
db_manager = DatabaseManager(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown events
    """
    # Startup
    print("Starting Transaction Service...")
    await db_manager.create_tables()
    print("Database connected")
    
    yield
    
    # Shutdown
    print("Shutting down Transaction Service...")
    await db_manager.close()
    print("Connections closed")


# Create FastAPI application
app = FastAPI(
    title="Transaction Service",
    description="Investment Portfolio Management - Transaction Service (Buy/Sell Operations)",
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


# Dependency overrides
async def get_db_session():
    """Provide database session"""
    async for session in db_manager.get_session():
        yield session


# Override dependencies in router
from router import get_transaction_service
from service import TransactionService
from repository import TransactionRepository


async def get_transaction_service_override(db=Depends(get_db_session)):
    """Override for transaction service dependency"""
    repository = TransactionRepository(db)
    return TransactionService(repository)


app.dependency_overrides[get_transaction_service] = get_transaction_service_override

# Include routers
app.include_router(transaction_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Transaction Service",
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
