"""
Transaction Service - Service Layer
Business logic for transaction operations
"""
from typing import List
import httpx
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.exceptions import ResourceNotFoundException, BusinessLogicException, InsufficientFundsException
from repository import TransactionRepository
from schemas import TransactionCreate, TransactionResponse, TransactionsByInvestorResponse
from models import TransactionType


class TransactionService:
    """
    Service layer for transaction business logic
    Implements validation and inter-service communication
    """
    
    # URLs for other microservices
    ASSET_SERVICE_URL = os.getenv("ASSET_SERVICE_URL", "http://localhost:8001")
    PORTFOLIO_SERVICE_URL = os.getenv("PORTFOLIO_SERVICE_URL", "http://localhost:8003")
    
    def __init__(self, repository: TransactionRepository):
        self.repository = repository
    
    async def create_transaction(self, transaction_data: TransactionCreate) -> TransactionResponse:
        """
        Create a new transaction with business logic validation
        
        This demonstrates microservices communication (Lab #4 requirement):
        - Validates investor exists (calls Portfolio Service)
        - Validates asset exists (calls Asset Service)
        - For BUY: Checks if investor has sufficient funds
        - For SELL: Checks if investor has sufficient asset holdings
        
        Args:
            transaction_data: Transaction creation data
            
        Returns:
            Created transaction response
            
        Raises:
            ResourceNotFoundException: If investor or asset not found
            InsufficientFundsException: If investor lacks funds
            BusinessLogicException: If validation fails
        """
        # Validate asset exists by calling Asset Service
        await self._validate_asset_exists(transaction_data.asset_id)
        
        # Validate investor exists by calling Portfolio Service
        await self._validate_investor_exists(transaction_data.investor_id)
        
        # Business logic validation
        if transaction_data.transaction_type == TransactionType.BUY:
            await self._validate_buy_transaction(transaction_data)
        elif transaction_data.transaction_type == TransactionType.SELL:
            await self._validate_sell_transaction(transaction_data)
        
        # Create transaction
        transaction = await self.repository.create(transaction_data)
        return TransactionResponse.model_validate(transaction)
    
    async def get_transaction_by_id(self, transaction_id: int) -> TransactionResponse:
        """
        Get transaction by ID
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Transaction response
            
        Raises:
            ResourceNotFoundException: If transaction not found
        """
        transaction = await self.repository.get_by_id(transaction_id)
        if not transaction:
            raise ResourceNotFoundException("Transaction", transaction_id)
        
        return TransactionResponse.model_validate(transaction)
    
    async def get_all_transactions(self, skip: int = 0, limit: int = 100) -> dict:
        """
        Get all transactions with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with total count and transaction list
        """
        transactions = await self.repository.get_all(skip, limit)
        total = await self.repository.count()
        
        return {
            "total": total,
            "transactions": [TransactionResponse.model_validate(t) for t in transactions]
        }
    
    async def get_investor_transactions(
        self,
        investor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> TransactionsByInvestorResponse:
        """
        Get all transactions for an investor with summary
        
        Args:
            investor_id: Investor identifier
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Investor transactions with financial summary
        """
        transactions = await self.repository.get_by_investor(investor_id, skip, limit)
        total_count = await self.repository.count_by_investor(investor_id)
        
        # Calculate financial summary
        total_invested = sum(
            t.total_amount for t in transactions if t.transaction_type == TransactionType.BUY
        )
        total_received = sum(
            t.total_amount for t in transactions if t.transaction_type == TransactionType.SELL
        )
        
        return TransactionsByInvestorResponse(
            investor_id=investor_id,
            total_transactions=total_count,
            total_invested=total_invested,
            total_received=total_received,
            net_amount=total_received - total_invested,
            transactions=[TransactionResponse.model_validate(t) for t in transactions]
        )
    
    async def _validate_asset_exists(self, asset_id: int) -> dict:
        """
        Validate that asset exists by calling Asset Service
        Demonstrates inter-service HTTP communication
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ASSET_SERVICE_URL}/assets/{asset_id}",
                    timeout=5.0
                )
                if response.status_code == 404:
                    raise ResourceNotFoundException("Asset", asset_id)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            # If Asset Service is not available, we'll continue (for development)
            print(f"Warning: Could not validate asset {asset_id}: {e}")
            return {"id": asset_id}  # Mock response
    
    async def _validate_investor_exists(self, investor_id: int) -> dict:
        """
        Validate that investor exists by calling Portfolio Service
        Demonstrates inter-service HTTP communication
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.PORTFOLIO_SERVICE_URL}/investors/{investor_id}",
                    timeout=5.0
                )
                if response.status_code == 404:
                    raise ResourceNotFoundException("Investor", investor_id)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            # If Portfolio Service is not available, we'll continue (for development)
            print(f"Warning: Could not validate investor {investor_id}: {e}")
            return {"id": investor_id, "balance": 100000.0}  # Mock response
    
    async def _validate_buy_transaction(self, transaction_data: TransactionCreate):
        """
        Validate BUY transaction
        Checks if investor has sufficient funds
        """
        investor = await self._validate_investor_exists(transaction_data.investor_id)
        total_cost = transaction_data.quantity * transaction_data.price_per_unit
        
        # Check if investor has sufficient balance
        investor_balance = investor.get("balance", 0)
        if investor_balance < total_cost:
            raise InsufficientFundsException(total_cost, investor_balance)
    
    async def _validate_sell_transaction(self, transaction_data: TransactionCreate):
        """
        Validate SELL transaction
        Checks if investor has sufficient asset holdings
        """
        holdings = await self.repository.get_investor_holdings(
            transaction_data.investor_id,
            transaction_data.asset_id
        )
        
        net_holdings = holdings["net_holdings"]
        if net_holdings < transaction_data.quantity:
            raise BusinessLogicException(
                f"Insufficient asset holdings: trying to sell {transaction_data.quantity}, "
                f"but only have {net_holdings}"
            )
