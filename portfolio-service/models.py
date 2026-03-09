"""
Portfolio Service - SQLAlchemy Models
Manages investors and their portfolio holdings
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import Base


class Investor(Base):
    """
    Investor (User) model
    
    Attributes:
        id: Primary key
        name: Full name of the investor
        email: Email address (unique)
        balance: Current available balance for investments
        created_at: Account creation timestamp
    """
    __tablename__ = "investors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to portfolio items
    portfolio_items = relationship("PortfolioItem", back_populates="investor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Investor(id={self.id}, name={self.name}, balance={self.balance})>"


class PortfolioItem(Base):
    """
    Portfolio item representing investor's holdings
    
    Attributes:
        id: Primary key
        investor_id: Foreign key to investor
        asset_id: Reference to asset (in Asset Service)
        quantity: Current quantity held
        average_buy_price: Average price at which assets were bought
        last_updated: Last update timestamp
    """
    __tablename__ = "portfolio_items"
    
    id = Column(Integer, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    asset_id = Column(Integer, nullable=False, index=True)  # Foreign key to Asset Service
    quantity = Column(Float, nullable=False, default=0.0)
    average_buy_price = Column(Float, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to investor
    investor = relationship("Investor", back_populates="portfolio_items")
    
    def __repr__(self):
        return f"<PortfolioItem(investor={self.investor_id}, asset={self.asset_id}, qty={self.quantity})>"
