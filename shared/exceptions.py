"""
Shared Exception Handlers
Global exception handling for all services
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any, Dict


class ResourceNotFoundException(Exception):
    """Raised when a requested resource is not found"""
    def __init__(self, resource: str, resource_id: Any):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with ID {resource_id} not found")


class InsufficientFundsException(Exception):
    """Raised when investor has insufficient funds for transaction"""
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(f"Insufficient funds: required {required}, available {available}")


class BusinessLogicException(Exception):
    """Generic business logic exception"""
    pass


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
    """Handle ResourceNotFoundException"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Resource Not Found",
            "message": str(exc),
            "resource": exc.resource,
            "resource_id": str(exc.resource_id)
        }
    )


async def insufficient_funds_handler(request: Request, exc: InsufficientFundsException) -> JSONResponse:
    """Handle InsufficientFundsException"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Insufficient Funds",
            "message": str(exc),
            "required": exc.required,
            "available": exc.available
        }
    )


async def business_logic_handler(request: Request, exc: BusinessLogicException) -> JSONResponse:
    """Handle BusinessLogicException"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Business Logic Error",
            "message": str(exc)
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input data",
            "details": exc.errors()
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


def register_exception_handlers(app):
    """Register all exception handlers to FastAPI app"""
    app.add_exception_handler(ResourceNotFoundException, resource_not_found_handler)
    app.add_exception_handler(InsufficientFundsException, insufficient_funds_handler)
    app.add_exception_handler(BusinessLogicException, business_logic_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
