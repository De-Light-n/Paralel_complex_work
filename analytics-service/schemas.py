"""
Analytics Service - Schemas
Generates reports and analytics from other services
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AssetAllocation(BaseModel):
    """Asset allocation in portfolio"""
    asset_id: int
    ticker: str
    name: str
    quantity: float
    current_value: float
    percentage: float


class PortfolioAnalytics(BaseModel):
    """Complete portfolio analytics"""
    investor_id: int
    investor_name: str
    total_balance: float
    total_invested: float
    current_portfolio_value: float
    total_profit_loss: float
    profit_loss_percentage: float
    asset_allocation: List[AssetAllocation]
    number_of_assets: int
    last_calculated: datetime


class RiskMetrics(BaseModel):
    """Risk assessment metrics"""
    investor_id: int
    diversification_score: float  # 0-100, higher is better
    concentration_risk: str  # LOW, MEDIUM, HIGH
    largest_holding_percentage: float
    number_of_assets: int
    risk_level: str  # CONSERVATIVE, MODERATE, AGGRESSIVE


class TransactionSummary(BaseModel):
    """Transaction summary statistics"""
    total_transactions: int
    total_buy_transactions: int
    total_sell_transactions: int
    total_amount_invested: float
    total_amount_received: float
    net_cash_flow: float
    average_transaction_size: float


class ComprehensiveReport(BaseModel):
    """Comprehensive investment report"""
    investor_id: int
    investor_name: str
    generated_at: datetime
    portfolio_analytics: PortfolioAnalytics
    risk_metrics: RiskMetrics
    transaction_summary: TransactionSummary
    recommendations: List[str]


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[dict] = None
