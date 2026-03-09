"""
Analytics Service - Router Layer
"""
from fastapi import APIRouter, Depends, status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from service import AnalyticsService
from schemas import PortfolioAnalytics, RiskMetrics, TransactionSummary, ComprehensiveReport

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service() -> AnalyticsService:
    """Dependency for injecting AnalyticsService"""
    return AnalyticsService()


@router.get(
    "/portfolio/{investor_id}",
    response_model=PortfolioAnalytics,
    status_code=status.HTTP_200_OK,
    summary="Get portfolio analytics"
)
async def get_portfolio_analytics(
    investor_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
) -> PortfolioAnalytics:
    """
    Get comprehensive portfolio analytics
    
    Aggregates data from Portfolio and Asset services to provide:
    - Total portfolio value
    - Profit/loss calculations
    - Asset allocation breakdown
    - Investment percentages
    """
    return await service.get_portfolio_analytics(investor_id)


@router.get(
    "/risk/{investor_id}",
    response_model=RiskMetrics,
    status_code=status.HTTP_200_OK,
    summary="Get risk assessment"
)
async def get_risk_assessment(
    investor_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
) -> RiskMetrics:
    """
    Get risk assessment for investor's portfolio
    
    Analyzes:
    - Diversification score
    - Concentration risk
    - Overall risk level (CONSERVATIVE, MODERATE, AGGRESSIVE)
    """
    return await service.get_risk_assessment(investor_id)


@router.get(
    "/transactions/{investor_id}",
    response_model=TransactionSummary,
    status_code=status.HTTP_200_OK,
    summary="Get transaction summary"
)
async def get_transaction_summary(
    investor_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
) -> TransactionSummary:
    """
    Get transaction summary statistics
    
    Provides:
    - Total number of transactions
    - Buy vs Sell breakdown
    - Total amounts invested and received
    - Net cash flow
    - Average transaction size
    """
    return await service.get_transaction_summary(investor_id)


@router.get(
    "/report/{investor_id}",
    response_model=ComprehensiveReport,
    status_code=status.HTTP_200_OK,
    summary="Generate comprehensive report"
)
async def generate_comprehensive_report(
    investor_id: int,
    service: AnalyticsService = Depends(get_analytics_service)
) -> ComprehensiveReport:
    """
    Generate comprehensive investment report
    
    This endpoint demonstrates microservices orchestration:
    - Calls Portfolio Service for holdings
    - Calls Asset Service for current prices
    - Calls Transaction Service for history
    - Aggregates all data into comprehensive report
    - Provides investment recommendations
    
    This is the main "report generation" requirement from the business logic
    """
    return await service.generate_comprehensive_report(investor_id)
