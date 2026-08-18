import httpx
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.intelligence.ai_engine import BaseAIProvider, MockAIProvider
from app.intelligence.models import AIAnalysis, MarketRegime, SentimentResult, FundamentalData
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterAIProvider(BaseAIProvider):
    """Production AI Provider using OpenRouter API with strictly grounded evidence."""
    
    def __init__(self):
        self.api_key = getattr(settings, "OPENROUTER_API_KEY", None)
        self.model = getattr(settings, "OPENROUTER_MODEL", "google/gemini-2.5-flash")
        self.base_url = getattr(settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
    def generate_analysis(
        self,
        symbol: str,
        timestamp: datetime,
        regime: MarketRegime,
        sentiment_evidence: List[SentimentResult],
        fundamental_evidence: List[FundamentalData],
        quantitative_evidence: Dict[str, Any]
    ) -> AIAnalysis:
        
        if not self.api_key:
            logger.error("OPENROUTER API KEY MISSING")
            return self._fail_safe(
                symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence,
                "REAL LLM BLOCKED — CREDENTIALS UNAVAILABLE", "SYSTEM_ERROR: AI Credentials missing"
            )
            
        try:
            # Grounded Input: Format strictly without future data leaks
            prompt = f"""
            You are a quantitative trading analysis assistant. Analyze the following grounded market evidence for {symbol} at {timestamp.isoformat()}.
            Do not assume future knowledge. Do not invent market facts. You must distinguish observation from inference.
            Provide a strictly formatted JSON response matching this schema exactly:
            {{
                "thesis": "string",
                "confidence": float (0-1),
                "bullish_factors": ["string"],
                "bearish_factors": ["string"],
                "risks": ["string"],
                "evidence": "string"
            }}
            
            Regime: {regime.trend_state}, Volatility: {regime.volatility_state}
            Quant: {json.dumps(quantitative_evidence)}
            Sentiment: {len(sentiment_evidence)} items
            Fundamentals: {len(fundamental_evidence)} items
            """
            
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": settings.FRONTEND_URL,
                    "X-Title": "Market 2.0"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": getattr(settings, "AI_MAX_TOKENS", 1024)
                },
                timeout=getattr(settings, "AI_REQUEST_TIMEOUT", 15.0)
            )
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded (429)")
                
            response.raise_for_status()
            
            data = response.json()
            content_str = data["choices"][0]["message"]["content"]
            
            # OpenRouter models might wrap JSON in markdown blocks
            if content_str.startswith("```json"):
                content_str = content_str[7:-3]
            elif content_str.startswith("```"):
                content_str = content_str[3:-3]
                
            content = json.loads(content_str.strip())
            
            actual_model = data.get("model", self.model)
            
            return AIAnalysis(
                symbol=symbol,
                timestamp=timestamp,
                market_context=f"{regime.trend_state}_{regime.volatility_state}",
                thesis=content.get("thesis", "No thesis provided"),
                confidence=content.get("confidence", 0.0),
                bullish_factors=content.get("bullish_factors", []),
                bearish_factors=content.get("bearish_factors", []),
                risks=content.get("risks", ["Unknown risk"]),
                evidence=content.get("evidence", "SUPPORTED BY DATA"),
                source="OPENROUTER",
                sentiment_evidence=sentiment_evidence,
                fundamental_evidence=fundamental_evidence,
                quantitative_evidence=quantitative_evidence,
                provider_id=self.model,
                actual_model=actual_model
            )
            
        except httpx.TimeoutException:
            logger.error("OpenRouter API Timeout")
            return self._fail_safe(
                symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence,
                "REAL LLM BLOCKED — API TIMEOUT", "SYSTEM_ERROR: OpenRouter API Timeout"
            )
        except Exception as e:
            logger.error(f"OpenRouter Provider failed: {e}")
            try:
                from app.data.database.session import SessionLocal
                from app.operations.incidents import incident_manager
                db = SessionLocal()
                incident_manager.log_incident(
                    db,
                    severity="ERROR",
                    category="AI_ERROR",
                    message=f"OpenRouter API failure: {str(e)}",
                    provider="openrouter"
                )
                db.close()
            except Exception:
                pass
                
            return self._fail_safe(
                symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence,
                "REAL LLM BLOCKED — API FAILURE", f"SYSTEM_ERROR: AI API Failure - {str(e)}"
            )

    def _fail_safe(self, symbol, timestamp, regime, sentiment_evidence, fundamental_evidence, quantitative_evidence, thesis, risk_msg):
        return AIAnalysis(
            symbol=symbol,
            timestamp=timestamp,
            market_context=f"{regime.trend_state}_{regime.volatility_state}",
            thesis=thesis,
            confidence=0.0,
            bullish_factors=[],
            bearish_factors=[],
            risks=[risk_msg],
            evidence="API_FAILURE",
            source="OPENROUTER",
            sentiment_evidence=sentiment_evidence,
            fundamental_evidence=fundamental_evidence,
            quantitative_evidence=quantitative_evidence,
            provider_id="openrouter"
        )
