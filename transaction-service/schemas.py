"""
Transaction Service - Pydantic Schemas
Request/Response models for API validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class TransactionBase(BaseModel):
    """Base schema with common transaction attributes"""
    investor_id: int = Field(..., gt=0, description="ID of the investor")
    asset_id: int = Field(..., gt=0, description="ID of the asset")
    transaction_type: TransactionType = Field(..., description="Type of transaction (BUY/SELL)")
    quantity: float = Field(..., gt=0, description="Quantity of units (must be positive)")
    price_per_unit: float = Field(..., gt=0, description="Price per unit at transaction time")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v
    
    @field_validator('price_per_unit')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price is positive"""
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    total_amount: float = Field(..., description="Total transaction amount (quantity * price)")
    timestamp: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode


class TransactionListResponse(BaseModel):
    """Schema for list of transactions response"""
    total: int
    transactions: list[TransactionResponse]


class TransactionsByInvestorResponse(BaseModel):
    """Schema for investor's transactions"""
    investor_id: int
    total_transactions: int
    total_invested: float
    total_received: float
    net_amount: float
    transactions: list[TransactionResponse]


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[dict] = None
