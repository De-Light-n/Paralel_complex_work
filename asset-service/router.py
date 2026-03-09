"""
Asset Service - Router Layer
FastAPI endpoints for asset management
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.cache import CacheManager
from repository import AssetRepository
from service import AssetService
from schemas import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse

router = APIRouter(prefix="/assets", tags=["Assets"])


# Dependency injection
async def get_asset_service(
    db: AsyncSession = Depends(),
    cache: CacheManager = Depends()
) -> AssetService:
    """
    Dependency for injecting AssetService
    This will be configured in main.py
    """
    repository = AssetRepository(db)
    return AssetService(repository, cache)


@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new asset",
    description="Create a new investment asset (stock, crypto, bond, commodity)"
)
async def create_asset(
    asset_data: AssetCreate,
    service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """
    Create a new asset
    
    - **ticker**: Unique ticker symbol (e.g., AAPL, BTC)
    - **name**: Full name of the asset
    - **asset_type**: Type of asset (STOCK, CRYPTO, BOND, COMMODITY)
    - **current_price**: Current market price (must be positive)
    
    Returns the created asset with ID and timestamps
    """
    return await service.create_asset(asset_data)


@router.get(
    "",
    response_model=AssetListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all assets",
    description="Retrieve a list of all available assets with pagination"
)
async def get_all_assets(
    skip: int = 0,
    limit: int = 100,
    service: AssetService = Depends(get_asset_service)
) -> AssetListResponse:
    """
    Get all assets with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    
    Returns total count and list of assets
    """
    result = await service.get_all_assets(skip, limit)
    return AssetListResponse(**result)


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get asset by ID",
    description="Retrieve a specific asset by ID (cached in Redis for performance)"
)
async def get_asset(
    asset_id: int,
    service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """
    Get asset by ID with Redis caching
    
    This endpoint demonstrates Lab #5 caching requirement:
    - First request: Fetches from database and caches in Redis
    - Subsequent requests: Returns from Redis cache (faster)
    - Cache TTL: 5 minutes
    
    - **asset_id**: Unique identifier of the asset
    
    Returns the asset details
    """
    return await service.get_asset_by_id(asset_id)


@router.put(
    "/{asset_id}",
    response_model=AssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Update asset",
    description="Update an existing asset (invalidates cache)"
)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    service: AssetService = Depends(get_asset_service)
) -> AssetResponse:
    """
    Update an existing asset
    
    - **asset_id**: Unique identifier of the asset
    - **asset_data**: Fields to update (all optional)
    
    Cache is automatically invalidated after update
    """
    return await service.update_asset(asset_id, asset_data)


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete asset",
    description="Delete an asset (invalidates cache)"
)
async def delete_asset(
    asset_id: int,
    service: AssetService = Depends(get_asset_service)
) -> None:
    """
    Delete an asset
    
    - **asset_id**: Unique identifier of the asset
    
    Cache is automatically invalidated after deletion
    """
    await service.delete_asset(asset_id)
