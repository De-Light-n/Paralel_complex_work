"""
Analytics Service - Main Application
Stateless service for generating reports
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.exceptions import register_exception_handlers
from router import router

# Create FastAPI application
app = FastAPI(
    title="Analytics Service",
    description="Investment Portfolio Management - Analytics & Reporting Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "service": "Analytics Service",
        "status": "running",
        "version": "1.0.0",
        "description": "Aggregates data from other services to generate reports"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "note": "This service is stateless and depends on other services"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
