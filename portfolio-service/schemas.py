"""
Portfolio Service - Pydantic Schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class InvestorBase(BaseModel):
    """Base schema for investor"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    balance: float = Field(default=0.0, ge=0, description="Account balance (must be non-negative)")


class InvestorCreate(InvestorBase):
    """Schema for creating a new investor"""
    pass


class InvestorUpdate(BaseModel):
    """Schema for updating an investor"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    balance: Optional[float] = Field(None, ge=0)


class InvestorResponse(InvestorBase):
    """Schema for investor response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioItemBase(BaseModel):
    """Base schema for portfolio item"""
    asset_id: int = Field(..., gt=0)
    quantity: float = Field(..., ge=0)
    average_buy_price: float = Field(..., gt=0)


class PortfolioItemResponse(PortfolioItemBase):
    """Schema for portfolio item response"""
    id: int
    investor_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True


class PortfolioItemWithAsset(PortfolioItemResponse):
    """Portfolio item with asset details (from Asset Service)"""
    asset_ticker: Optional[str] = None
    asset_name: Optional[str] = None
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None


class CashOperationRequest(BaseModel):
    """Request schema for deposit/withdraw operations"""
    amount: float = Field(..., gt=0)


class PortfolioTradeRequest(BaseModel):
    """Request schema for buy/sell portfolio trade"""
    asset_id: int = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)


class PortfolioTradeResponse(BaseModel):
    """Response schema for portfolio trade operations"""
    investor: InvestorResponse
    holding: PortfolioItemWithAsset
    total_amount: float
    operation: str


class PortfolioSummary(BaseModel):
    """Complete portfolio summary"""
    investor: InvestorResponse
    holdings: List[PortfolioItemWithAsset]
    total_invested: float
    current_total_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[dict] = None
