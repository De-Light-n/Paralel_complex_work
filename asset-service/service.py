"""
Asset Service - Service Layer
Business logic with Redis caching (Lab #5 requirement)
"""
from typing import List, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.cache import CacheManager
from shared.exceptions import ResourceNotFoundException, BusinessLogicException
from repository import AssetRepository
from schemas import AssetCreate, AssetUpdate, AssetResponse
from models import Asset


class AssetService:
    """
    Service layer for asset business logic
    Implements caching strategy using Redis
    """
    
    CACHE_PREFIX = "asset"
    CACHE_TTL = 300  # 5 minutes
    
    def __init__(self, repository: AssetRepository, cache_manager: Optional[CacheManager] = None):
        self.repository = repository
        self.cache = cache_manager
    
    async def create_asset(self, asset_data: AssetCreate) -> AssetResponse:
        """
        Create a new asset
        
        Args:
            asset_data: Asset creation data
            
        Returns:
            Created asset response
            
        Raises:
            BusinessLogicException: If ticker already exists
        """
        # Check if ticker already exists
        existing = await self.repository.get_by_ticker(asset_data.ticker)
        if existing:
            raise BusinessLogicException(f"Asset with ticker {asset_data.ticker} already exists")
        
        # Create asset
        asset = await self.repository.create(asset_data)
        
        # Cache the new asset
        if self.cache:
            cache_key = f"{self.CACHE_PREFIX}:{asset.id}"
            await self.cache.set(cache_key, self._asset_to_dict(asset), ttl=self.CACHE_TTL)
        
        return AssetResponse.model_validate(asset)
    
    async def get_asset_by_id(self, asset_id: int) -> AssetResponse:
        """
        Get asset by ID with Redis caching
        This is the key Lab #5 requirement - demonstrating cache usage
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Asset response
            
        Raises:
            ResourceNotFoundException: If asset not found
        """
        cache_key = f"{self.CACHE_PREFIX}:{asset_id}"
        
        # Try to get from cache first
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                print(f"Cache HIT for asset {asset_id}")
                return AssetResponse(**cached_data)
            print(f"Cache MISS for asset {asset_id}")
        
        # If not in cache, get from database
        asset = await self.repository.get_by_id(asset_id)
        if not asset:
            raise ResourceNotFoundException("Asset", asset_id)
        
        # Store in cache for next time
        if self.cache:
            await self.cache.set(cache_key, self._asset_to_dict(asset), ttl=self.CACHE_TTL)
        
        return AssetResponse.model_validate(asset)
    
    async def get_all_assets(self, skip: int = 0, limit: int = 100) -> dict:
        """
        Get all assets with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with total count and asset list
        """
        assets = await self.repository.get_all(skip, limit)
        total = await self.repository.count()
        
        return {
            "total": total,
            "assets": [AssetResponse.model_validate(a) for a in assets]
        }
    
    async def update_asset(self, asset_id: int, asset_data: AssetUpdate) -> AssetResponse:
        """
        Update an existing asset
        
        Args:
            asset_id: Asset identifier
            asset_data: Update data
            
        Returns:
            Updated asset response
            
        Raises:
            ResourceNotFoundException: If asset not found
        """
        asset = await self.repository.get_by_id(asset_id)
        if not asset:
            raise ResourceNotFoundException("Asset", asset_id)
        
        updated_asset = await self.repository.update(asset, asset_data)
        
        # Invalidate cache
        if self.cache:
            cache_key = f"{self.CACHE_PREFIX}:{asset_id}"
            await self.cache.delete(cache_key)
        
        return AssetResponse.model_validate(updated_asset)
    
    async def delete_asset(self, asset_id: int) -> None:
        """
        Delete an asset
        
        Args:
            asset_id: Asset identifier
            
        Raises:
            ResourceNotFoundException: If asset not found
        """
        asset = await self.repository.get_by_id(asset_id)
        if not asset:
            raise ResourceNotFoundException("Asset", asset_id)
        
        await self.repository.delete(asset)
        
        # Invalidate cache
        if self.cache:
            cache_key = f"{self.CACHE_PREFIX}:{asset_id}"
            await self.cache.delete(cache_key)
    
    def _asset_to_dict(self, asset: Asset) -> dict:
        """Convert Asset model to dictionary for caching"""
        return {
            "id": asset.id,
            "ticker": asset.ticker,
            "name": asset.name,
            "asset_type": asset.asset_type.value,
            "current_price": asset.current_price,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "updated_at": asset.updated_at.isoformat() if asset.updated_at else None
        }
