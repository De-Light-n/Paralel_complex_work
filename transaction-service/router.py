"""
Transaction Service - Router Layer
FastAPI endpoints for transaction management
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from repository import TransactionRepository
from service import TransactionService
from schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    TransactionsByInvestorResponse
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

async def get_db_stub():
    """Stub for db session"""
    pass

# Dependency injection
async def get_transaction_service(db: AsyncSession = Depends(get_db_stub)) -> TransactionService:
    """
    Dependency for injecting TransactionService
    This will be configured in main.py
    """
    repository = TransactionRepository(db)
    return TransactionService(repository)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new transaction",
    description="Execute a buy or sell transaction with validation"
)
async def create_transaction(
    transaction_data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Create a new transaction (BUY or SELL)
    
    This endpoint demonstrates the core business logic:
    - **BUY**: Validates investor has sufficient funds
    - **SELL**: Validates investor has sufficient asset holdings
    - Communicates with Asset Service to validate asset
    - Communicates with Portfolio Service to validate investor
    
    Required fields:
    - **investor_id**: ID of the investor making the transaction
    - **asset_id**: ID of the asset being traded
    - **transaction_type**: BUY or SELL
    - **quantity**: Number of units to trade (must be positive)
    - **price_per_unit**: Price per unit at transaction time
    - **notes**: Optional transaction notes
    
    Returns the created transaction with calculated total amount
    """
    return await service.create_transaction(transaction_data)


@router.get(
    "",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all transactions",
    description="Retrieve all transactions with pagination"
)
async def get_all_transactions(
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
) -> TransactionListResponse:
    """
    Get all transactions with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    
    Returns transactions ordered by timestamp (newest first)
    """
    result = await service.get_all_transactions(skip, limit)
    return TransactionListResponse(**result)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get transaction by ID",
    description="Retrieve a specific transaction by ID"
)
async def get_transaction(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service)
) -> TransactionResponse:
    """
    Get transaction by ID
    
    - **transaction_id**: Unique identifier of the transaction
    
    Returns the transaction details
    """
    return await service.get_transaction_by_id(transaction_id)


@router.get(
    "/investor/{investor_id}",
    response_model=TransactionsByInvestorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get investor's transactions",
    description="Retrieve all transactions for a specific investor with financial summary"
)
async def get_investor_transactions(
    investor_id: int,
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
) -> TransactionsByInvestorResponse:
    """
    Get all transactions for an investor with financial summary
    
    - **investor_id**: ID of the investor
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    
    Returns:
    - List of transactions
    - Total invested (all BUY transactions)
    - Total received (all SELL transactions)
    - Net amount (received - invested)
    """
    return await service.get_investor_transactions(investor_id, skip, limit)
