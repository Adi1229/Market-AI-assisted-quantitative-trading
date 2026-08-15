from sqlalchemy import Column, String, Float, DateTime, Boolean, BigInteger, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.data.database.session import Base
import datetime

class Instrument(Base):
    __tablename__ = "instruments"

    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    active = Column(Boolean, default=True)

class OHLCVData(Base):
    __tablename__ = "ohlcv_data"

    timestamp = Column(DateTime(timezone=True), primary_key=True, index=True)
    symbol = Column(String, primary_key=True, index=True)
    timeframe = Column(String, primary_key=True, default="1d")
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Phase 5: Engine Models

class TradeOpportunityDB(Base):
    __tablename__ = "trade_opportunities"
    
    opportunity_id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    decision_mode = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    strategy_evidence = Column(JSON, nullable=True)
    ai_evidence = Column(JSON, nullable=True)
    
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderDB(Base):
    __tablename__ = "paper_orders"
    
    order_id = Column(String, primary_key=True, index=True)
    opportunity_id = Column(String, ForeignKey("trade_opportunities.opportunity_id"))
    instrument_id = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    order_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    fill_price = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    filled_at = Column(DateTime(timezone=True), nullable=True)

class PositionDB(Base):
    __tablename__ = "paper_positions"
    
    id = Column(String, primary_key=True, index=True)
    instrument_id = Column(String, index=True, nullable=False)
    direction = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    opened_at = Column(DateTime(timezone=True), nullable=False)

class UserDecisionDB(Base):
    __tablename__ = "user_decisions"
    
    action_id = Column(String, primary_key=True, index=True)
    opportunity_id = Column(String, ForeignKey("trade_opportunities.opportunity_id"))
    action = Column(String, nullable=False) # TAKE_TRADE, IGNORE
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Phase 7: Hardening Models

class PortfolioStateDB(Base):
    __tablename__ = "portfolio_state"
    
    id = Column(String, primary_key=True, index=True) # typically "virtual"
    cash = Column(Float, nullable=False, default=100000.0)
    realized_pnl = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class IdempotencyKeyDB(Base):
    __tablename__ = "idempotency_keys"
    
    idempotency_key = Column(String, primary_key=True, index=True)
    opportunity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
