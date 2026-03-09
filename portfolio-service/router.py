"""
Portfolio Service - Router Layer
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from repository import PortfolioRepository
from service import PortfolioService
from schemas import InvestorCreate, InvestorUpdate, InvestorResponse, PortfolioSummary

router = APIRouter()


async def get_portfolio_service(db: AsyncSession = Depends()) -> PortfolioService:
    """Dependency for injecting PortfolioService"""
    repository = PortfolioRepository(db)
    return PortfolioService(repository)


@router.post(
    "/investors",
    response_model=InvestorResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Investors"]
)
async def create_investor(
    investor_data: InvestorCreate,
    service: PortfolioService = Depends(get_portfolio_service)
) -> InvestorResponse:
    """Create a new investor"""
    return await service.create_investor(investor_data)


@router.get(
    "/investors",
    response_model=List[InvestorResponse],
    status_code=status.HTTP_200_OK,
    tags=["Investors"]
)
async def get_all_investors(
    skip: int = 0,
    limit: int = 100,
    service: PortfolioService = Depends(get_portfolio_service)
) -> List[InvestorResponse]:
    """Get all investors"""
    return await service.get_all_investors(skip, limit)


@router.get(
    "/investors/{investor_id}",
    response_model=InvestorResponse,
    status_code=status.HTTP_200_OK,
    tags=["Investors"]
)
async def get_investor(
    investor_id: int,
    service: PortfolioService = Depends(get_portfolio_service)
) -> InvestorResponse:
    """Get investor by ID"""
    return await service.get_investor_by_id(investor_id)


@router.put(
    "/investors/{investor_id}",
    response_model=InvestorResponse,
    status_code=status.HTTP_200_OK,
    tags=["Investors"]
)
async def update_investor(
    investor_id: int,
    investor_data: InvestorUpdate,
    service: PortfolioService = Depends(get_portfolio_service)
) -> InvestorResponse:
    """Update an investor"""
    return await service.update_investor(investor_id, investor_data)


@router.get(
    "/portfolio/{investor_id}",
    response_model=PortfolioSummary,
    status_code=status.HTTP_200_OK,
    tags=["Portfolio"]
)
async def get_portfolio(
    investor_id: int,
    service: PortfolioService = Depends(get_portfolio_service)
) -> PortfolioSummary:
    """
    Get complete portfolio for an investor
    
    Returns holdings with current values and profit/loss calculations
    Communicates with Asset Service to get current prices
    """
    return await service.get_portfolio(investor_id)
