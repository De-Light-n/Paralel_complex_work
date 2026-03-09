"""
Transaction Service - Repository Layer
Data access layer for transaction operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from models import Transaction, TransactionType
from schemas import TransactionCreate


class TransactionRepository:
    """
    Repository pattern for Transaction data access
    Handles all database operations
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, transaction_data: TransactionCreate) -> Transaction:
        """
        Create a new transaction
        
        Args:
            transaction_data: Transaction creation data
            
        Returns:
            Created transaction instance
        """
        # Calculate total amount
        total_amount = transaction_data.quantity * transaction_data.price_per_unit
        
        transaction = Transaction(
            investor_id=transaction_data.investor_id,
            asset_id=transaction_data.asset_id,
            transaction_type=transaction_data.transaction_type,
            quantity=transaction_data.quantity,
            price_per_unit=transaction_data.price_per_unit,
            total_amount=total_amount,
            notes=transaction_data.notes
        )
        self.session.add(transaction)
        await self.session.flush()
        await self.session.refresh(transaction)
        return transaction
    
    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Transaction instance or None if not found
        """
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """
        Get all transactions with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of transactions
        """
        result = await self.session.execute(
            select(Transaction)
            .order_by(Transaction.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_investor(
        self,
        investor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Get all transactions for a specific investor
        
        Args:
            investor_id: Investor identifier
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of transactions
        """
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.investor_id == investor_id)
            .order_by(Transaction.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_asset(
        self,
        asset_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        """
        Get all transactions for a specific asset
        
        Args:
            asset_id: Asset identifier
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of transactions
        """
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.asset_id == asset_id)
            .order_by(Transaction.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_investor_holdings(self, investor_id: int, asset_id: int) -> dict:
        """
        Calculate investor's holdings for a specific asset
        
        Args:
            investor_id: Investor identifier
            asset_id: Asset identifier
            
        Returns:
            Dictionary with buy/sell quantities and net holdings
        """
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.investor_id == investor_id,
                    Transaction.asset_id == asset_id
                )
            )
        )
        transactions = list(result.scalars().all())
        
        buy_quantity = sum(
            t.quantity for t in transactions if t.transaction_type == TransactionType.BUY
        )
        sell_quantity = sum(
            t.quantity for t in transactions if t.transaction_type == TransactionType.SELL
        )
        
        return {
            "buy_quantity": buy_quantity,
            "sell_quantity": sell_quantity,
            "net_holdings": buy_quantity - sell_quantity
        }
    
    async def count(self) -> int:
        """
        Get total count of transactions
        
        Returns:
            Total number of transactions
        """
        result = await self.session.execute(select(Transaction))
        return len(list(result.scalars().all()))
    
    async def count_by_investor(self, investor_id: int) -> int:
        """
        Get count of transactions for an investor
        
        Args:
            investor_id: Investor identifier
            
        Returns:
            Number of transactions
        """
        result = await self.session.execute(
            select(Transaction).where(Transaction.investor_id == investor_id)
        )
        return len(list(result.scalars().all()))
