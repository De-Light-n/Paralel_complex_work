"""
Asset Service - Pydantic Schemas
Request/Response models for API validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration"""
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    BOND = "BOND"
    COMMODITY = "COMMODITY"


class AssetBase(BaseModel):
    """Base schema with common asset attributes"""
    ticker: str = Field(..., min_length=1, max_length=10, description="Asset ticker symbol")
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the asset")
    asset_type: AssetType = Field(..., description="Type of asset")
    current_price: float = Field(..., gt=0, description="Current market price (must be positive)")
    
    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Convert ticker to uppercase"""
        return v.upper()


class AssetCreate(AssetBase):
    """Schema for creating a new asset"""
    pass


class AssetUpdate(BaseModel):
    """Schema for updating an existing asset"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    asset_type: Optional[AssetType] = None
    current_price: Optional[float] = Field(None, gt=0)


class AssetResponse(AssetBase):
    """Schema for asset response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy


class AssetListResponse(BaseModel):
    """Schema for list of assets response"""
    total: int
    assets: list[AssetResponse]


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[dict] = None
