import asyncio
import os
import sys
from datetime import datetime
import json
import httpx

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.intelligence.openrouter_provider import OpenRouterAIProvider
from app.intelligence.models import MarketRegime, SentimentResult

async def run_minimal_test(api_key, model, base_url):
    print("\n[TEST 1] Minimal Connectivity Test")
    print(f" - Model: {model}")
    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Return exactly: {\"status\": \"ok\"}"}],
                "max_tokens": settings.AI_MAX_TOKENS
            },
            timeout=settings.AI_REQUEST_TIMEOUT
        )
        if response.status_code == 402:
            print(f" - HTTP 402: REAL OPENROUTER INFERENCE = BLOCKED — PAYMENT REQUIRED")
            return False
        elif response.status_code == 429:
            print(f" - HTTP 429: REAL OPENROUTER INFERENCE = BLOCKED — RATE LIMITED")
            return False
        elif response.status_code == 404:
            print(f" - HTTP 404: REAL OPENROUTER INFERENCE = BLOCKED — MODEL UNAVAILABLE")
            return False
            
        response.raise_for_status()
        data = response.json()
        print(f" - Result: {data['choices'][0]['message']['content'].strip()}")
        return True
    except Exception as e:
        print(f" - Error: {str(e)}")
        return False

async def run_grounded_test():
    print("\n[TEST 2] Grounded Market Test")
    provider = OpenRouterAIProvider()
    
    symbol = "RELIANCE.NS"
    timestamp = datetime.now()
    regime = MarketRegime(
        symbol=symbol,
        timestamp=timestamp,
        trend_state="Bullish",
        volatility_state="Normal",
        momentum_state="Neutral"
    )
    sentiment = [SentimentResult(news_id="VALIDATION", symbol=symbol, score=0.8, label="Bullish", provider_id="Mock")]
    quant = {"SMA_20": 2450.0, "SMA_50": 2400.0, "RSI_14": 58.5}
    
    analysis = provider.generate_analysis(
        symbol=symbol,
        timestamp=timestamp,
        regime=regime,
        sentiment_evidence=sentiment,
        fundamental_evidence=[],
        quantitative_evidence=quant
    )
    
    print("\n==================================================")
    print("STRUCTURED OUTPUT RESULT")
    print("==================================================")
    print(f"Provider    : {analysis.source}")
    print(f"Model       : {analysis.provider_id}")
    print(f"Actual Model: {analysis.actual_model}")
    print(f"Confidence  : {analysis.confidence}")
    print(f"Thesis      : {analysis.thesis}")
    
    if analysis.evidence == "API_FAILURE":
        print("\n[STATUS] REAL OPENROUTER INFERENCE = FAILED")
    elif analysis.thesis == "REAL LLM BLOCKED — CREDENTIALS UNAVAILABLE":
        print("\n[STATUS] REAL OPENROUTER INFERENCE = BLOCKED")
    else:
        print("\n[STATUS] REAL OPENROUTER INFERENCE = VERIFIED")
        
    print("\n[SAFETY] NOTE: No trades were executed. LIVE execution remains locked.")

async def main():
    print("==================================================")
    print("OPENROUTER FREE MODEL VALIDATION")
    print("==================================================")
    
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        print("[ERROR] API Key missing.")
        return
        
    print(f"[CONFIG] AI_MAX_TOKENS: {settings.AI_MAX_TOKENS}")
    print(f"[CONFIG] AI_REQUEST_TIMEOUT: {settings.AI_REQUEST_TIMEOUT}")
    print(f"[CONFIG] AI_MAX_REQUESTS_PER_RUN: {settings.AI_MAX_REQUESTS_PER_RUN}")
    
    if await run_minimal_test(api_key, settings.OPENROUTER_MODEL, settings.OPENROUTER_BASE_URL):
        await run_grounded_test()
    else:
        print("\n[STATUS] Exiting early due to minimal test failure.")

if __name__ == "__main__":
    asyncio.run(main())
