"""
Asset Service - SQLAlchemy Models
Defines the database structure for assets
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import Base


class AssetType(str, enum.Enum):
    """Enum for asset types"""
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    BOND = "BOND"
    COMMODITY = "COMMODITY"


class Asset(Base):
    """
    Asset model representing investment instruments
    
    Attributes:
        id: Primary key
        ticker: Asset ticker symbol (e.g., AAPL, BTC)
        name: Full name of the asset
        asset_type: Type of asset (STOCK, CRYPTO, etc.)
        current_price: Current market price
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    current_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Asset(id={self.id}, ticker={self.ticker}, price={self.current_price})>"
