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
    PortfolioItemWithAsset,
    CashOperationRequest,
    PortfolioTradeRequest,
    PortfolioTradeResponse
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

        holdings: List[PortfolioItemWithAsset] = []
        total_invested = 0.0
        current_total = 0.0

        for item in items:
            holding = await self._build_holding_with_asset(item)

            invested_value = item.quantity * item.average_buy_price
            current_price = holding.current_price if holding.current_price is not None else item.average_buy_price
            current_value = item.quantity * current_price
            profit_loss = current_value - invested_value
            profit_loss_pct = (profit_loss / invested_value * 100) if invested_value > 0 else 0

            holding.current_value = current_value
            holding.profit_loss = profit_loss
            holding.profit_loss_percentage = profit_loss_pct
            holdings.append(holding)

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

    async def get_holdings(self, investor_id: int) -> List[PortfolioItemWithAsset]:
        """Get all holdings for an investor with asset details"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)

        items = await self.repository.get_portfolio_items(investor_id)
        holdings: List[PortfolioItemWithAsset] = []
        for item in items:
            holdings.append(await self._build_holding_with_asset(item))
        return holdings

    async def get_holding_by_asset(self, investor_id: int, asset_id: int) -> PortfolioItemWithAsset:
        """Get detailed holding for a specific asset"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)

        item = await self.repository.get_portfolio_item(investor_id, asset_id)
        if not item or item.quantity <= 0:
            raise ResourceNotFoundException("Portfolio asset", asset_id)

        return await self._build_holding_with_asset(item)

    async def deposit_funds(self, investor_id: int, data: CashOperationRequest) -> InvestorResponse:
        """Deposit funds to investor balance"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)

        updated = await self.repository.update_investor_balance(investor, investor.balance + data.amount)
        return InvestorResponse.model_validate(updated)

    async def withdraw_funds(self, investor_id: int, data: CashOperationRequest) -> InvestorResponse:
        """Withdraw funds from investor balance"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)

        if investor.balance < data.amount:
            raise BusinessLogicException(
                f"Insufficient balance: requested {data.amount}, available {investor.balance}"
            )

        updated = await self.repository.update_investor_balance(investor, investor.balance - data.amount)
        return InvestorResponse.model_validate(updated)

    async def buy_asset(self, investor_id: int, trade: PortfolioTradeRequest) -> PortfolioTradeResponse:
        """Buy asset and update investor balance/holding"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)

        total_cost = trade.quantity * trade.price_per_unit
        if investor.balance < total_cost:
            raise BusinessLogicException(
                f"Insufficient balance for buy: required {total_cost}, available {investor.balance}"
            )

        current_item = await self.repository.get_portfolio_item(investor_id, trade.asset_id)

        if current_item:
            new_quantity = current_item.quantity + trade.quantity
            new_avg_price = (
                (current_item.quantity * current_item.average_buy_price) + total_cost
            ) / new_quantity
        else:
            new_quantity = trade.quantity
            new_avg_price = trade.price_per_unit

        item = await self.repository.upsert_portfolio_item(
            investor_id=investor_id,
            asset_id=trade.asset_id,
            quantity=new_quantity,
            average_price=new_avg_price
        )

        updated_investor = await self.repository.update_investor_balance(
            investor,
            investor.balance - total_cost
        )

        return PortfolioTradeResponse(
            investor=InvestorResponse.model_validate(updated_investor),
            holding=await self._build_holding_with_asset(item),
            total_amount=total_cost,
            operation="BUY"
        )

    async def sell_asset(self, investor_id: int, trade: PortfolioTradeRequest) -> PortfolioTradeResponse:
        """Sell asset and update investor balance/holding"""
        investor = await self.repository.get_investor_by_id(investor_id)
        if not investor:
            raise ResourceNotFoundException("Investor", investor_id)

        item = await self.repository.get_portfolio_item(investor_id, trade.asset_id)
        if not item or item.quantity <= 0:
            raise BusinessLogicException(f"No holdings for asset {trade.asset_id}")

        if item.quantity < trade.quantity:
            raise BusinessLogicException(
                f"Insufficient holdings: requested {trade.quantity}, available {item.quantity}"
            )

        total_proceeds = trade.quantity * trade.price_per_unit
        new_quantity = item.quantity - trade.quantity

        if new_quantity == 0:
            await self.repository.delete_portfolio_item(item)
            holding = PortfolioItemWithAsset(
                id=item.id,
                investor_id=item.investor_id,
                asset_id=item.asset_id,
                quantity=0.0,
                average_buy_price=item.average_buy_price,
                last_updated=item.last_updated,
                current_price=trade.price_per_unit,
                current_value=0.0,
                profit_loss=0.0,
                profit_loss_percentage=0.0
            )
        else:
            updated_item = await self.repository.upsert_portfolio_item(
                investor_id=investor_id,
                asset_id=trade.asset_id,
                quantity=new_quantity,
                average_price=item.average_buy_price
            )
            holding = await self._build_holding_with_asset(updated_item)

        updated_investor = await self.repository.update_investor_balance(
            investor,
            investor.balance + total_proceeds
        )

        return PortfolioTradeResponse(
            investor=InvestorResponse.model_validate(updated_investor),
            holding=holding,
            total_amount=total_proceeds,
            operation="SELL"
        )

    async def _build_holding_with_asset(self, item) -> PortfolioItemWithAsset:
        """Build holding DTO enriched with Asset Service data"""
        asset_data = await self._get_asset_data(item.asset_id)
        invested_value = item.quantity * item.average_buy_price
        current_price = asset_data.get("current_price", item.average_buy_price)
        current_value = item.quantity * current_price
        profit_loss = current_value - invested_value
        profit_loss_pct = (profit_loss / invested_value * 100) if invested_value > 0 else 0

        return PortfolioItemWithAsset(
            id=item.id,
            investor_id=item.investor_id,
            asset_id=item.asset_id,
            quantity=item.quantity,
            average_buy_price=item.average_buy_price,
            last_updated=item.last_updated,
            asset_ticker=asset_data.get("ticker"),
            asset_name=asset_data.get("name"),
            current_price=current_price,
            current_value=current_value,
            profit_loss=profit_loss,
            profit_loss_percentage=profit_loss_pct
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
