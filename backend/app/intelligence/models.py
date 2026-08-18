from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class NewsItem(BaseModel):
    id: str
    headline: str
    source: str
    timestamp: datetime
    symbols: List[str] = Field(default_factory=list)
    text: Optional[str] = None
    url: Optional[str] = None

class SentimentResult(BaseModel):
    news_id: str
    symbol: Optional[str] = None
    score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score from -1.0 to 1.0")
    label: str = Field(..., description="Bullish, Bearish, or Neutral")
    provider_id: str

class FundamentalData(BaseModel):
    symbol: str
    timestamp: datetime
    metric: str
    value: float
    provider_id: str

class MarketRegime(BaseModel):
    symbol: str
    timestamp: datetime
    trend_state: str = Field(..., description="E.g., Bullish, Bearish, Neutral")
    volatility_state: str = Field(..., description="E.g., High, Low")
    momentum_state: str = Field(..., description="E.g., Overbought, Oversold, Neutral")
    features_used: Dict[str, float] = Field(default_factory=dict)

class AIAnalysis(BaseModel):
    symbol: str
    timestamp: datetime
    market_context: str
    thesis: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bullish_factors: List[str] = Field(default_factory=list)
    bearish_factors: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    evidence: str = Field(..., description="SUPPORTED BY DATA or INSUFFICIENT EVIDENCE")
    source: str = Field(..., description="E.g., REAL or MOCK")
    sentiment_evidence: List[SentimentResult] = Field(default_factory=list)
    fundamental_evidence: List[FundamentalData] = Field(default_factory=list)
    quantitative_evidence: Dict[str, Any] = Field(default_factory=dict)
    provider_id: str

class StrategyRanking(BaseModel):
    strategy_id: str
    strategy_version: str
    score: float
    rank: int
    supporting_features: Dict[str, float] = Field(default_factory=dict)
    model_id: str
