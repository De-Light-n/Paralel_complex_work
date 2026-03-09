"""
Transaction Service - SQLAlchemy Models
Defines the database structure for transactions
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
import enum
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import Base


class TransactionType(str, enum.Enum):
    """Enum for transaction types"""
    BUY = "BUY"
    SELL = "SELL"


class Transaction(Base):
    """
    Transaction model representing buy/sell operations
    
    Attributes:
        id: Primary key
        investor_id: Reference to investor in Portfolio Service
        asset_id: Reference to asset in Asset Service
        transaction_type: BUY or SELL
        quantity: Number of units traded
        price_per_unit: Price at the moment of transaction
        total_amount: Total transaction amount (quantity * price_per_unit)
        timestamp: When the transaction occurred
        notes: Optional notes about the transaction
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, nullable=False, index=True)  # Foreign key to Portfolio Service
    asset_id = Column(Integer, nullable=False, index=True)  # Foreign key to Asset Service
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String(500), nullable=True)
    
    def __repr__(self):
        return (f"<Transaction(id={self.id}, type={self.transaction_type}, "
                f"investor={self.investor_id}, asset={self.asset_id}, qty={self.quantity})>")
