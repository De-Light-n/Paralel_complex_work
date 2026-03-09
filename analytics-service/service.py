"""
Analytics Service - Service Layer
Aggregates data from other microservices to generate reports
"""
import httpx
import os
from datetime import datetime
from typing import List
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.exceptions import ResourceNotFoundException, BusinessLogicException
from schemas import (
    PortfolioAnalytics,
    AssetAllocation,
    RiskMetrics,
    TransactionSummary,
    ComprehensiveReport
)


class AnalyticsService:
    """
    Service for generating analytics and reports
    Demonstrates microservices orchestration
    """
    
    ASSET_SERVICE_URL = os.getenv("ASSET_SERVICE_URL", "http://localhost:8001")
    PORTFOLIO_SERVICE_URL = os.getenv("PORTFOLIO_SERVICE_URL", "http://localhost:8003")
    TRANSACTION_SERVICE_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8002")
    
    async def get_portfolio_analytics(self, investor_id: int) -> PortfolioAnalytics:
        """
        Generate portfolio analytics by aggregating data from services
        """
        # Get portfolio data from Portfolio Service
        portfolio = await self._fetch_portfolio(investor_id)
        
        # Extract data
        investor = portfolio["investor"]
        holdings = portfolio["holdings"]
        
        # Calculate asset allocation
        allocations: List[AssetAllocation] = []
        total_value = portfolio["current_total_value"]
        
        for holding in holdings:
            allocations.append(AssetAllocation(
                asset_id=holding["asset_id"],
                ticker=holding.get("asset_ticker", "N/A"),
                name=holding.get("asset_name", "Unknown"),
                quantity=holding["quantity"],
                current_value=holding.get("current_value", 0),
                percentage=(holding.get("current_value", 0) / total_value * 100) if total_value > 0 else 0
            ))
        
        return PortfolioAnalytics(
            investor_id=investor_id,
            investor_name=investor["name"],
            total_balance=investor["balance"],
            total_invested=portfolio["total_invested"],
            current_portfolio_value=total_value,
            total_profit_loss=portfolio["total_profit_loss"],
            profit_loss_percentage=portfolio["total_profit_loss_percentage"],
            asset_allocation=allocations,
            number_of_assets=len(holdings),
            last_calculated=datetime.now()
        )
    
    async def get_risk_assessment(self, investor_id: int) -> RiskMetrics:
        """
        Assess investment risk based on diversification
        """
        # Get portfolio analytics
        analytics = await self.get_portfolio_analytics(investor_id)
        
        # Calculate risk metrics
        num_assets = analytics.number_of_assets
        
        # Diversification score (simplified): more assets = better diversification
        if num_assets >= 10:
            diversification_score = 90.0
        elif num_assets >= 5:
            diversification_score = 70.0
        elif num_assets >= 3:
            diversification_score = 50.0
        else:
            diversification_score = 30.0
        
        # Find largest holding
        largest_holding = 0.0
        if analytics.asset_allocation:
            largest_holding = max(a.percentage for a in analytics.asset_allocation)
        
        # Determine concentration risk
        if largest_holding > 50:
            concentration = "HIGH"
        elif largest_holding > 30:
            concentration = "MEDIUM"
        else:
            concentration = "LOW"
        
        # Determine overall risk level
        if diversification_score >= 70 and concentration == "LOW":
            risk_level = "CONSERVATIVE"
        elif diversification_score >= 50:
            risk_level = "MODERATE"
        else:
            risk_level = "AGGRESSIVE"
        
        return RiskMetrics(
            investor_id=investor_id,
            diversification_score=diversification_score,
            concentration_risk=concentration,
            largest_holding_percentage=largest_holding,
            number_of_assets=num_assets,
            risk_level=risk_level
        )
    
    async def get_transaction_summary(self, investor_id: int) -> TransactionSummary:
        """
        Generate transaction summary from Transaction Service
        """
        transactions_data = await self._fetch_transactions(investor_id)
        
        transactions = transactions_data.get("transactions", [])
        
        buy_count = sum(1 for t in transactions if t["transaction_type"] == "BUY")
        sell_count = sum(1 for t in transactions if t["transaction_type"] == "SELL")
        
        total_invested = sum(t["total_amount"] for t in transactions if t["transaction_type"] == "BUY")
        total_received = sum(t["total_amount"] for t in transactions if t["transaction_type"] == "SELL")
        
        avg_size = (total_invested + total_received) / len(transactions) if transactions else 0
        
        return TransactionSummary(
            total_transactions=len(transactions),
            total_buy_transactions=buy_count,
            total_sell_transactions=sell_count,
            total_amount_invested=total_invested,
            total_amount_received=total_received,
            net_cash_flow=total_received - total_invested,
            average_transaction_size=avg_size
        )
    
    async def generate_comprehensive_report(self, investor_id: int) -> ComprehensiveReport:
        """
        Generate comprehensive investment report
        Aggregates all analytics
        """
        # Fetch all analytics
        portfolio_analytics = await self.get_portfolio_analytics(investor_id)
        risk_metrics = await self.get_risk_assessment(investor_id)
        transaction_summary = await self.get_transaction_summary(investor_id)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            portfolio_analytics,
            risk_metrics,
            transaction_summary
        )
        
        return ComprehensiveReport(
            investor_id=investor_id,
            investor_name=portfolio_analytics.investor_name,
            generated_at=datetime.now(),
            portfolio_analytics=portfolio_analytics,
            risk_metrics=risk_metrics,
            transaction_summary=transaction_summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(
        self,
        portfolio: PortfolioAnalytics,
        risk: RiskMetrics,
        transactions: TransactionSummary
    ) -> List[str]:
        """Generate investment recommendations"""
        recommendations = []
        
        # Diversification recommendations
        if risk.number_of_assets < 3:
            recommendations.append(
                "Consider diversifying your portfolio by investing in more assets to reduce risk"
            )
        
        # Concentration risk
        if risk.concentration_risk == "HIGH":
            recommendations.append(
                f"Your largest holding represents {risk.largest_holding_percentage:.1f}% of your portfolio. "
                "Consider rebalancing to reduce concentration risk"
            )
        
        # Profitability
        if portfolio.total_profit_loss < 0:
            recommendations.append(
                f"Your portfolio is currently showing a loss of {abs(portfolio.total_profit_loss):.2f}. "
                "Consider reviewing your investment strategy"
            )
        elif portfolio.profit_loss_percentage > 20:
            recommendations.append(
                f"Excellent performance! Your portfolio has gained {portfolio.profit_loss_percentage:.2f}%. "
                "Consider taking some profits"
            )
        
        # Activity level
        if transactions.total_transactions < 5:
            recommendations.append(
                "Low trading activity detected. Consider gradually building your portfolio"
            )
        
        # Cash balance
        if portfolio.total_balance > portfolio.current_portfolio_value * 0.5:
            recommendations.append(
                "You have significant cash balance. Consider investing more to maximize returns"
            )
        
        if not recommendations:
            recommendations.append("Your portfolio appears well-balanced. Keep monitoring your investments")
        
        return recommendations
    
    async def _fetch_portfolio(self, investor_id: int) -> dict:
        """Fetch portfolio from Portfolio Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.PORTFOLIO_SERVICE_URL}/portfolio/{investor_id}",
                    timeout=10.0
                )
                if response.status_code == 404:
                    raise ResourceNotFoundException("Investor", investor_id)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise BusinessLogicException(f"Failed to fetch portfolio: {str(e)}")
    
    async def _fetch_transactions(self, investor_id: int) -> dict:
        """Fetch transactions from Transaction Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TRANSACTION_SERVICE_URL}/transactions/investor/{investor_id}",
                    timeout=10.0
                )
                if response.status_code == 404:
                    return {"transactions": []}
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            print(f"Warning: Could not fetch transactions: {e}")
            return {"transactions": []}
