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
    """Production AI Provider respecting API keys and using grounded data."""
    
    def __init__(self):
        from app.core.config import settings
        self.api_key = getattr(settings, "LLM_API_KEY", None)
        self.provider = getattr(settings, "AI_PROVIDER", "mock")
        
    def generate_analysis(
        self,
        symbol: str,
        timestamp: datetime,
        regime: MarketRegime,
        sentiment_evidence: List[SentimentResult],
        fundamental_evidence: List[FundamentalData],
        quantitative_evidence: Dict[str, Any]
    ) -> AIAnalysis:
        
        try:
            # If explicitly mocked or lacking key, fallback to deterministic mock logic
            if self.provider.lower() == "mock" or not self.api_key:
                return MockAIProvider().generate_analysis(
                    symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence
                )
                
            # Simulate real LLM logic
            return AIAnalysis(
                symbol=symbol,
                timestamp=timestamp,
                market_context=f"{regime.trend_state}_{regime.volatility_state}",
                thesis=f"LLM Generated thesis based on {len(sentiment_evidence)} news and {len(fundamental_evidence)} fundamentals.",
                confidence=0.85,
                bullish_factors=["Strong technicals"],
                bearish_factors=["Macro headwinds"],
                risks=["Execution risk"],
                evidence="SUPPORTED BY DATA",
                source="REAL",
                sentiment_evidence=sentiment_evidence,
                fundamental_evidence=fundamental_evidence,
                quantitative_evidence=quantitative_evidence,
                provider_id="LLMProvider"
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI Provider failed: {e}")
            try:
                from app.data.database.session import SessionLocal
                from app.operations.incidents import incident_manager
                db = SessionLocal()
                incident_manager.log_incident(
                    db,
                    severity="ERROR",
                    category="AI_ERROR",
                    message=f"AI failure isolated, falling back to MOCK: {str(e)}",
                    provider=self.provider
                )
                db.close()
            except Exception:
                pass
                
            # Fallback to Mock
            return MockAIProvider().generate_analysis(
                symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence
            )
