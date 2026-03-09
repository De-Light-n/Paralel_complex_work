"""
Portfolio Service - Repository Layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from models import Investor, PortfolioItem
from schemas import InvestorCreate, InvestorUpdate


class PortfolioRepository:
    """Repository for investor and portfolio data access"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # Investor operations
    async def create_investor(self, investor_data: InvestorCreate) -> Investor:
        """Create a new investor"""
        investor = Investor(
            name=investor_data.name,
            email=investor_data.email,
            balance=investor_data.balance
        )
        self.session.add(investor)
        await self.session.flush()
        await self.session.refresh(investor)
        return investor
    
    async def get_investor_by_id(self, investor_id: int) -> Optional[Investor]:
        """Get investor by ID"""
        result = await self.session.execute(
            select(Investor).where(Investor.id == investor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_investor_by_email(self, email: str) -> Optional[Investor]:
        """Get investor by email"""
        result = await self.session.execute(
            select(Investor).where(Investor.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all_investors(self, skip: int = 0, limit: int = 100) -> List[Investor]:
        """Get all investors"""
        result = await self.session.execute(
            select(Investor).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_investor(self, investor: Investor, investor_data: InvestorUpdate) -> Investor:
        """Update an investor"""
        update_data = investor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(investor, field, value)
        await self.session.flush()
        await self.session.refresh(investor)
        return investor
    
    # Portfolio operations
    async def get_portfolio_items(self, investor_id: int) -> List[PortfolioItem]:
        """Get all portfolio items for an investor"""
        result = await self.session.execute(
            select(PortfolioItem)
            .where(PortfolioItem.investor_id == investor_id)
            .where(PortfolioItem.quantity > 0)
        )
        return list(result.scalars().all())
    
    async def get_portfolio_item(self, investor_id: int, asset_id: int) -> Optional[PortfolioItem]:
        """Get specific portfolio item"""
        result = await self.session.execute(
            select(PortfolioItem).where(
                PortfolioItem.investor_id == investor_id,
                PortfolioItem.asset_id == asset_id
            )
        )
        return result.scalar_one_or_none()
    
    async def upsert_portfolio_item(
        self,
        investor_id: int,
        asset_id: int,
        quantity: float,
        average_price: float
    ) -> PortfolioItem:
        """Create or update portfolio item"""
        existing = await self.get_portfolio_item(investor_id, asset_id)
        
        if existing:
            existing.quantity = quantity
            existing.average_buy_price = average_price
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        else:
            item = PortfolioItem(
                investor_id=investor_id,
                asset_id=asset_id,
                quantity=quantity,
                average_buy_price=average_price
            )
            self.session.add(item)
            await self.session.flush()
            await self.session.refresh(item)
            return item
