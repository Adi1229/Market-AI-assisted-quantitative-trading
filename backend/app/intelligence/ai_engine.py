from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from app.intelligence.models import AIAnalysis, MarketRegime, SentimentResult, FundamentalData

class BaseAIProvider(ABC):
    """Abstract interface for structured AI analysis."""
    
    @abstractmethod
    def generate_analysis(
        self,
        symbol: str,
        timestamp: datetime,
        regime: MarketRegime,
        sentiment_evidence: List[SentimentResult],
        fundamental_evidence: List[FundamentalData],
        quantitative_evidence: Dict[str, Any]
    ) -> AIAnalysis:
        pass

class MockAIProvider(BaseAIProvider):
    """Deterministic mock AI provider for offline testing."""
    
    def generate_analysis(
        self,
        symbol: str,
        timestamp: datetime,
        regime: MarketRegime,
        sentiment_evidence: List[SentimentResult],
        fundamental_evidence: List[FundamentalData],
        quantitative_evidence: Dict[str, Any]
    ) -> AIAnalysis:
        
        # Analyze completeness of evidence
        missing_evidence = []
        if not sentiment_evidence:
            missing_evidence.append("Sentiment")
        if not fundamental_evidence:
            missing_evidence.append("Fundamentals")
            
        # Determine confidence based on evidence completeness
        base_confidence = 0.8
        confidence = base_confidence - (0.3 * len(missing_evidence))
        confidence = max(0.0, min(1.0, confidence))
        
        # Formulate thesis based on deterministic rules
        thesis = f"Market is currently in a {regime.trend_state} trend with {regime.volatility_state} volatility."
        
        bullish_sentiments = sum(1 for s in sentiment_evidence if s.label == "Bullish")
        bearish_sentiments = sum(1 for s in sentiment_evidence if s.label == "Bearish")
        
        if bullish_sentiments > bearish_sentiments:
            thesis += " Sentiment is net positive."
        elif bearish_sentiments > bullish_sentiments:
            thesis += " Sentiment is net negative."
            
        if missing_evidence:
            thesis += f" Missing evidence: {', '.join(missing_evidence)}."
            
        risks = ["Market volatility could increase"]
        if regime.trend_state == "Neutral":
            risks.append("Lack of clear trend direction")
            
        return AIAnalysis(
            symbol=symbol,
            timestamp=timestamp,
            market_context=f"{regime.trend_state}_{regime.volatility_state}",
            thesis=thesis,
            confidence=confidence,
            risks=risks,
            sentiment_evidence=sentiment_evidence,
            fundamental_evidence=fundamental_evidence,
            quantitative_evidence=quantitative_evidence,
            provider_id="MockAI"
        )
