"""
Portfolio Service - Service Layer
"""
import httpx
import os
import sys
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.exceptions import ResourceNotFoundException, BusinessLogicException
from repository import PortfolioRepository
from schemas import (
    InvestorCreate,
    InvestorUpdate,
    InvestorResponse,
    PortfolioSummary,
    PortfolioItemWithAsset
)


class PortfolioService:
    """Service layer for portfolio operations"""
    
    ASSET_SERVICE_URL = os.getenv("ASSET_SERVICE_URL", "http://localhost:8001")
    
    def __init__(self, repository: PortfolioRepository):
        self.repository = repository
    
    async def create_investor(self, investor_data: InvestorCreate) -> InvestorResponse:
        """Create a new investor"""
        existing = await self.repository.get_investor_by_email(investor_data.email)
        if existing:
            raise BusinessLogicException(f"Investor with email {investor_data.email} already exists")
        
        investor = await self.repository.create_investor(investor_data)
        return InvestorResponse.model_validate(investor)
    
    async def get_investor_by_id(self, investor_id: int) -> InvestorResponse:
        """Get investor by ID"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)
        return InvestorResponse.model_validate(investor)
    
    async def get_all_investors(self, skip: int = 0, limit: int = 100) -> List[InvestorResponse]:
        """Get all investors"""
        investors = await self.repository.get_all_investors(skip, limit)
        return [InvestorResponse.model_validate(i) for i in investors]
    
    async def update_investor(self, investor_id: int, investor_data: InvestorUpdate) -> InvestorResponse:
        """Update an investor"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)
        
        updated = await self.repository.update_investor(investor, investor_data)
        return InvestorResponse.model_validate(updated)
    
    async def get_portfolio(self, investor_id: int) -> PortfolioSummary:
        """
        Get complete portfolio with current values
        Calls Asset Service to get current prices
        """
        # Get investor
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)
        
        # Get portfolio items
        items = await self.repository.get_portfolio_items(investor_id)
        
        # Enrich with asset data
        holdings: List[PortfolioItemWithAsset] = []
        total_invested = 0.0
        current_total = 0.0
        
        for item in items:
            asset_data = await self._get_asset_data(item.asset_id)
            
            invested_value = item.quantity * item.average_buy_price
            current_value = item.quantity * asset_data.get("current_price", item.average_buy_price)
            profit_loss = current_value - invested_value
            profit_loss_pct = (profit_loss / invested_value * 100) if invested_value > 0 else 0
            
            holdings.append(PortfolioItemWithAsset(
                id=item.id,
                investor_id=item.investor_id,
                asset_id=item.asset_id,
                quantity=item.quantity,
                average_buy_price=item.average_buy_price,
                last_updated=item.last_updated,
                asset_ticker=asset_data.get("ticker"),
                asset_name=asset_data.get("name"),
                current_price=asset_data.get("current_price"),
                current_value=current_value,
                profit_loss=profit_loss,
                profit_loss_percentage=profit_loss_pct
            ))
            
            total_invested += invested_value
            current_total += current_value
        
        total_pl = current_total - total_invested
        total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0
        
        return PortfolioSummary(
            investor=InvestorResponse.model_validate(investor),
            holdings=holdings,
            total_invested=total_invested,
            current_total_value=current_total,
            total_profit_loss=total_pl,
            total_profit_loss_percentage=total_pl_pct
        )
    
    async def _get_asset_data(self, asset_id: int) -> dict:
        """Get asset data from Asset Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ASSET_SERVICE_URL}/assets/{asset_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"Warning: Could not fetch asset {asset_id}: {e}")
        
        # Return mock data if service unavailable
        return {
            "id": asset_id,
            "ticker": f"ASSET{asset_id}",
            "name": "Unknown Asset",
            "current_price": 100.0
        }
