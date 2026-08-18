from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

# Common Responses
class MessageResponse(BaseModel):
    message: str

# Strategies
class StrategyResponse(BaseModel):
    id: str
    name: str
    version: str
    description: str
    status: str

# Opportunities
class StrategyEvidenceResponse(BaseModel):
    strategy_id: str
    strategy_name: str
    signal_direction: int
    signal_score: float
    signal_type: str

class AIEvidenceResponse(BaseModel):
    provider_id: str
    direction: str
    ai_score: float
    market_context: str
    thesis: str

class OpportunityResponse(BaseModel):
    opportunity_id: str
    symbol: str
    timestamp: datetime
    decision_mode: str
    direction: str
    confidence_score: float
    status: str
    suggested_entry: Optional[float] = None
    market_regime: str
    risk_level: str
    strategy_evidence: Optional[StrategyEvidenceResponse] = None
    ai_evidence: Optional[AIEvidenceResponse] = None
    reasoning: List[str] = []

# Approval
class ApproveRequest(BaseModel):
    current_price: float

class RejectRequest(BaseModel):
    current_price: float

# Portfolio
class PositionResponse(BaseModel):
    instrument_id: str
    direction: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    opened_at: datetime

class OrderResponse(BaseModel):
    order_id: str
    opportunity_id: Optional[str] = None
    instrument_id: str
    direction: str
    order_type: str
    quantity: float
    status: str
    fill_price: Optional[float] = None
    commission: Optional[float] = None
    slippage: Optional[float] = None
    created_at: datetime
    filled_at: Optional[datetime] = None

class PortfolioSummaryResponse(BaseModel):
    total_value: float
    cash: float
    positions_value: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    exposure_pct: float
    drawdown: float
    max_drawdown: float
    open_positions: int
    total_trades: int

# Configuration
class DecisionModeUpdate(BaseModel):
    mode: str

class ExecutionModeUpdate(BaseModel):
    mode: str

# Backtesting
class BacktestRequest(BaseModel):
    strategy_id: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000.0

class BacktestResponse(BaseModel):
    backtest_id: str
    strategy_id: str
    symbol: str
    total_return: float
    cagr: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profit_factor: float

# Phase 12: Watchlist & Analytics
class WatchlistCreate(BaseModel):
    name: str

class WatchlistResponse(BaseModel):
    id: str
    name: str
    instruments: List[str]
    created_at: datetime

class PerformanceAnalyticsResponse(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_win: float
    average_loss: float
    profit_factor: float
    ai_agreement_rate: float
    strategy_metrics: Dict[str, Any]
