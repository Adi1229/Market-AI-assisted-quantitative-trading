from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class DecisionMode(str, Enum):
    STRATEGY_ONLY = "STRATEGY_ONLY"
    AI_ONLY = "AI_ONLY"
    HYBRID = "HYBRID"

class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    FLAT = "FLAT"

class OpportunityStatus(str, Enum):
    CREATED = "CREATED"
    RISK_APPROVED = "RISK_APPROVED"
    RISK_REJECTED = "RISK_REJECTED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    EXECUTION_FAILED = "EXECUTION_FAILED"

class DataReference(BaseModel):
    source_type: str
    description: str
    timestamp: datetime
    value: Optional[str] = None

class StrategyEvidence(BaseModel):
    strategy_id: str
    strategy_name: str
    strategy_version: str
    parameters: Dict[str, Any]
    signal_type: str
    signal_score: float
    features_used: Dict[str, float]
    explanation: str

class AIEvidence(BaseModel):
    ai_model_id: str
    ai_model_version: str
    direction: str
    ai_score: float
    reasoning: List[str]
    retrieved_facts: List[str]
    computed_values: Dict[str, float]
    model_inference: str
    uncertainty: str
    evidence_sources: List[DataReference]

class TradeOpportunity(BaseModel):
    opportunity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    instrument_id: str
    timestamp: datetime
    
    decision_mode: DecisionMode
    direction: Direction
    confidence_score: float
    
    strategy_evidence: Optional[StrategyEvidence] = None
    ai_evidence: Optional[AIEvidence] = None
    
    market_regime: str
    news_sentiment: Optional[str] = None
    fundamental_context: Optional[str] = None
    
    suggested_entry: Optional[float] = None
    suggested_stop_loss: Optional[float] = None
    suggested_target: Optional[float] = None
    suggested_position_size: Optional[float] = None
    risk_level: str
    
    reasoning: List[str]
    data_references: List[DataReference]
    expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    status: OpportunityStatus = OpportunityStatus.CREATED

class RiskDecision(BaseModel):
    approved: bool
    reason: str

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class ExecutionOrder(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    opportunity_id: str
    instrument_id: str
    direction: str
    order_type: str
    quantity: float
    limit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    fill_price: Optional[float] = None
    commission: Optional[float] = None
    slippage: Optional[float] = None

class ExecutionPosition(BaseModel):
    instrument_id: str
    direction: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    opened_at: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PortfolioSummary(BaseModel):
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
