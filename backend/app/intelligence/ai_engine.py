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
        
        bullish_factors = []
        bearish_factors = []
        
        if regime.trend_state == "Bullish":
            bullish_factors.append("Bullish macro trend identified")
        elif regime.trend_state == "Bearish":
            bearish_factors.append("Bearish macro trend identified")
            
        if bullish_sentiments > bearish_sentiments:
            thesis += " Sentiment is net positive."
            bullish_factors.append("Net positive news sentiment")
        elif bearish_sentiments > bullish_sentiments:
            thesis += " Sentiment is net negative."
            bearish_factors.append("Net negative news sentiment")
            
        if missing_evidence:
            thesis += f" Missing evidence: {', '.join(missing_evidence)}."
            evidence = "INSUFFICIENT EVIDENCE"
        else:
            evidence = "SUPPORTED BY DATA"
            
        risks = ["Market volatility could increase"]
        if regime.trend_state == "Neutral":
            risks.append("Lack of clear trend direction")
            
        return AIAnalysis(
            symbol=symbol,
            timestamp=timestamp,
            market_context=f"{regime.trend_state}_{regime.volatility_state}",
            thesis=thesis,
            confidence=confidence,
            bullish_factors=bullish_factors,
            bearish_factors=bearish_factors,
            risks=risks,
            evidence=evidence,
            source="MOCK",
            sentiment_evidence=sentiment_evidence,
            fundamental_evidence=fundamental_evidence,
            quantitative_evidence=quantitative_evidence,
            provider_id="MockAI"
        )

class ConfigurableLLMProvider(BaseAIProvider):
    """Production AI Provider delegating to specific implementations based on config."""
    
    def __init__(self):
        from app.core.config import settings
        self.provider_type = getattr(settings, "AI_PROVIDER", "mock").lower()
        
    def generate_analysis(
        self,
        symbol: str,
        timestamp: datetime,
        regime: MarketRegime,
        sentiment_evidence: List[SentimentResult],
        fundamental_evidence: List[FundamentalData],
        quantitative_evidence: Dict[str, Any]
    ) -> AIAnalysis:
        
        if self.provider_type == "openrouter":
            from app.intelligence.openrouter_provider import OpenRouterAIProvider
            return OpenRouterAIProvider().generate_analysis(
                symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence
            )
            
        # Default mock behavior
        return MockAIProvider().generate_analysis(
            symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence
        )
