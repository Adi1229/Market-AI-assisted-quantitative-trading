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
    session_id = Column(String, ForeignKey("paper_sessions.id"), nullable=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    decision_mode = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # New Phase 12 fields
    strategy_version = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)
    market_regime = Column(String, nullable=True)
    
    strategy_evidence = Column(JSON, nullable=True)
    ai_evidence = Column(JSON, nullable=True)
    reasoning = Column(JSON, nullable=True)
    
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

# Phase 12: Productization Models

class PaperTradingSessionDB(Base):
    __tablename__ = "paper_sessions"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    starting_capital = Column(Float, nullable=False)
    current_capital = Column(Float, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False) # CREATED, ACTIVE, PAUSED, COMPLETED, CANCELLED
    execution_mode = Column(String, nullable=False, default="PAPER")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class WatchlistDB(Base):
    __tablename__ = "watchlists"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class WatchlistInstrumentDB(Base):
    __tablename__ = "watchlist_instruments"
    
    id = Column(String, primary_key=True, index=True)
    watchlist_id = Column(String, ForeignKey("watchlists.id"), nullable=False)
    symbol = Column(String, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class PaperTradingJournalDB(Base):
    __tablename__ = "paper_trading_journal"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("paper_sessions.id"), nullable=True, index=True)
    opportunity_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    
    realized_pnl = Column(Float, nullable=True)
    
    strategy = Column(String, nullable=True)
    strategy_version = Column(String, nullable=True)
    decision_mode = Column(String, nullable=True)
    ai_score = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)
    regime = Column(String, nullable=True)
    
    fees = Column(Float, nullable=True, default=0.0)
    slippage = Column(Float, nullable=True, default=0.0)
    data_source = Column(String, nullable=True)
    ai_source = Column(String, nullable=True)
    
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Phase 14: Operations and Reliability Models

class IncidentDB(Base):
    __tablename__ = "incidents"
    
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    severity = Column(String, nullable=False, index=True) # INFO, WARNING, ERROR, CRITICAL
    category = Column(String, nullable=False, index=True) # DATA_STALE, DATA_GAP, PROVIDER_429, DATABASE_ERROR, etc.
    instrument = Column(String, nullable=True, index=True)
    provider = Column(String, nullable=True)
    message = Column(String, nullable=False)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

class HeartbeatDB(Base):
    __tablename__ = "heartbeats"
    
    id = Column(String, primary_key=True, index=True) # usually "system" or specific component
    last_processed = Column(DateTime(timezone=True), nullable=True)
    last_market_update = Column(DateTime(timezone=True), nullable=True)
    last_strategy_eval = Column(DateTime(timezone=True), nullable=True)
    last_opportunity = Column(DateTime(timezone=True), nullable=True)
    last_risk_eval = Column(DateTime(timezone=True), nullable=True)
    last_paper_execution = Column(DateTime(timezone=True), nullable=True)
    current_session = Column(String, nullable=True)
    provider_status = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MarketHealthDB(Base):
    __tablename__ = "market_health"
    
    symbol = Column(String, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    latest_candle_ts = Column(DateTime(timezone=True), nullable=True)
    latest_completed_ts = Column(DateTime(timezone=True), nullable=True)
    data_age_seconds = Column(Float, nullable=True)
    expected_interval_seconds = Column(Float, nullable=True)
    candles_received = Column(BigInteger, default=0)
    missing_candles = Column(BigInteger, default=0)
    duplicate_candles = Column(BigInteger, default=0)
    invalid_candles = Column(BigInteger, default=0)
    status = Column(String, nullable=False, default="UNKNOWN") # HEALTHY, DEGRADED, STALE, ERROR, MARKET_CLOSED, UNKNOWN
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ProviderHealthDB(Base):
    __tablename__ = "provider_health"
    
    provider_id = Column(String, primary_key=True, index=True)
    success_count = Column(BigInteger, default=0)
    error_429_count = Column(BigInteger, default=0)
    timeout_count = Column(BigInteger, default=0)
    auth_error_count = Column(BigInteger, default=0)
    empty_response_count = Column(BigInteger, default=0)
    malformed_response_count = Column(BigInteger, default=0)
    connection_error_count = Column(BigInteger, default=0)
    last_successful_request = Column(DateTime(timezone=True), nullable=True)
    consecutive_failures = Column(BigInteger, default=0)
    status = Column(String, nullable=False, default="HEALTHY")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
