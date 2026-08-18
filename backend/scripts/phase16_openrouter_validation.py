import asyncio
import os
import sys
from datetime import datetime
import json

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.intelligence.openrouter_provider import OpenRouterAIProvider
from app.intelligence.models import MarketRegime, SentimentResult, FundamentalData

async def run_validation():
    print("==================================================")
    print("OPENROUTER REAL LLM VALIDATION")
    print("==================================================")
    
    # 1. & 2. Verify Config
    print(f"\n[CONFIG] AI_PROVIDER: {settings.AI_PROVIDER}")
    if settings.AI_PROVIDER != "openrouter":
        print("[ERROR] AI_PROVIDER must be 'openrouter' for this test.")
        return

    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY is missing.")
        return
        
    model = settings.OPENROUTER_MODEL
    print(f"[CONFIG] OPENROUTER_MODEL: {model}")
    print("[CONFIG] OPENROUTER_API_KEY: <HIDDEN_FOR_SECURITY>")
    
    # 3. Build controlled snapshot
    print("\n[EVIDENCE] Building Grounded Evidence...")
    symbol = "RELIANCE.NS"
    timestamp = datetime.now()
    regime = MarketRegime(
        symbol=symbol,
        timestamp=timestamp,
        trend_state="Bullish",
        volatility_state="Normal",
        momentum_state="Neutral"
    )
    sentiment_evidence = [
        SentimentResult(
            news_id="VALIDATION_1",
            symbol=symbol,
            score=0.75,
            label="Bullish",
            provider_id="NewsProvider"
        )
    ]
    fundamental_evidence = []
    quantitative_evidence = {
        "SMA_20": 2450.0,
        "SMA_50": 2400.0,
        "RSI_14": 58.5,
        "ATR_14": 20.1
    }
    
    print(f" - Symbol: {symbol}")
    print(f" - Timestamp: {timestamp}")
    print(f" - Quant Features: {len(quantitative_evidence)} metrics")
    print(f" - Sentiment: {len(sentiment_evidence)} items")
    
    # 4 & 5. Initialize Provider & Call OpenRouter
    print("\n[API] Sending to OpenRouter API (This may take a few seconds)...")
    provider = OpenRouterAIProvider()
    
    analysis = provider.generate_analysis(
        symbol=symbol,
        timestamp=timestamp,
        regime=regime,
        sentiment_evidence=sentiment_evidence,
        fundamental_evidence=fundamental_evidence,
        quantitative_evidence=quantitative_evidence
    )
    
    # 6. & 7. Validate and Print Output
    print("\n==================================================")
    print("RESPONSE VALIDATION")
    print("==================================================")
    print(f"Provider    : {analysis.source}")
    print(f"Model Used  : {analysis.provider_id}")
    print(f"Confidence  : {analysis.confidence}")
    print(f"Thesis      : {analysis.thesis}")
    print(f"Bull Factors: {analysis.bullish_factors}")
    print(f"Bear Factors: {analysis.bearish_factors}")
    print(f"Risks       : {analysis.risks}")
    
    if analysis.evidence == "API_FAILURE":
        print("\n[RESULT] FAIL - API FAILURE DETECTED.")
    elif analysis.thesis == "REAL LLM BLOCKED — CREDENTIALS UNAVAILABLE":
        print("\n[RESULT] FAIL - BLOCKED BY CREDENTIALS.")
    else:
        print("\n[RESULT] SUCCESS - AI VALIDATION PASSED.")
        
    print("\n[SAFETY] NOTE: No trades were executed. LIVE execution remains locked.")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_validation())
