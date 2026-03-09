"""
Asset Service - Repository Layer
Data access layer for asset operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models import Asset
from schemas import AssetCreate, AssetUpdate


class AssetRepository:
    """
    Repository pattern for Asset data access
    Separates database operations from business logic
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, asset_data: AssetCreate) -> Asset:
        """
        Create a new asset
        
        Args:
            asset_data: Asset creation data
            
        Returns:
            Created asset instance
        """
        asset = Asset(
            ticker=asset_data.ticker,
            name=asset_data.name,
            asset_type=asset_data.asset_type,
            current_price=asset_data.current_price
        )
        self.session.add(asset)
        await self.session.flush()
        await self.session.refresh(asset)
        return asset
    
    async def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        Get asset by ID
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Asset instance or None if not found
        """
        result = await self.session.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ticker(self, ticker: str) -> Optional[Asset]:
        """
        Get asset by ticker symbol
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Asset instance or None if not found
        """
        result = await self.session.execute(
            select(Asset).where(Asset.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        """
        Get all assets with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of assets
        """
        result = await self.session.execute(
            select(Asset).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """
        Get total count of assets
        
        Returns:
            Total number of assets
        """
        result = await self.session.execute(select(Asset))
        return len(list(result.scalars().all()))
    
    async def update(self, asset: Asset, asset_data: AssetUpdate) -> Asset:
        """
        Update an existing asset
        
        Args:
            asset: Asset instance to update
            asset_data: Update data
            
        Returns:
            Updated asset instance
        """
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        
        await self.session.flush()
        await self.session.refresh(asset)
        return asset
    
    async def delete(self, asset: Asset) -> None:
        """
        Delete an asset
        
        Args:
            asset: Asset instance to delete
        """
        await self.session.delete(asset)
        await self.session.flush()
