import asyncio
from datetime import datetime, timezone, timedelta
from app.api.dependencies import (
    get_market_data_provider, 
    get_news_provider, 
    get_fundamental_provider,
    get_signal_engine,
    get_workflow_orchestrator,
    get_portfolio
)
from app.data.ingestion import DataIngestionService
from app.data.database.session import SessionLocal
from app.intelligence.models import AIAnalysis
from app.strategies.base import StrategySignal
from app.engine.models import DecisionMode

async def main():
    print("==================================================")
    print("PHASE 8 E2E REAL DATA VALIDATION")
    print("==================================================")
    
    # 1. Instantiate Providers
    market_provider = get_market_data_provider()
    news_provider = get_news_provider()
    fundamental_provider = get_fundamental_provider()
    
    print(f"Market Provider: {market_provider.provider_id}")
    if market_provider.provider_id != "yfinance":
        print("ERROR: DATA_PROVIDER=real is not working. Provider is mock.")
        return
        
    symbol = "RELIANCE.NS"
    print(f"Target Symbol: {symbol}")
    
    # 2. Database Ingestion
    db = SessionLocal()
    try:
        print("\n--- Testing Data Ingestion ---")
        ingestion = DataIngestionService(market_provider, db)
        start = datetime.now(timezone.utc) - timedelta(days=5)
        end = datetime.now(timezone.utc)
        
        rows = ingestion.ingest_historical_data(symbol, "1d", start, end)
        print(f"SUCCESS: Ingested {rows} rows for {symbol} to TimescaleDB.")
        
        # 3. Intelligence (News & Fundamentals)
        print("\n--- Testing News Provider ---")
        news = news_provider.fetch_news(symbol, start, end)
        print(f"SUCCESS: Fetched {len(news)} news items.")
        if news:
            print(f"Sample Headline: {news[0].headline}")
            
        print("\n--- Testing Fundamentals Provider ---")
        funds = fundamental_provider.fetch_fundamentals(symbol, end)
        print(f"SUCCESS: Fetched {len(funds)} fundamental metrics.")
        if funds:
            print(f"Sample Metric: {funds[0].metric} = {funds[0].value}")
            
        # 4. Generate AI Analysis & Signal (Mocked as per requirements)
        import uuid
        unique_symbol = f"TEST_SYM_{uuid.uuid4().hex[:6]}"
        print(f"\n--- Generating Mock AI Analysis & Strategy Signal for {unique_symbol} ---")
        signal_engine = get_signal_engine()
        orchestrator = get_workflow_orchestrator()
        
        strategy_sig = StrategySignal(
            symbol=unique_symbol, strategy_id="momentum_v1", strategy_version="1", 
            direction=1, features={"RSI": 60.0}, timestamp=datetime.now(timezone.utc)
        )
        ai_analysis = AIAnalysis(
            symbol=unique_symbol, timestamp=datetime.now(timezone.utc), market_context="Bullish trend indicated by news and fundamentals.",
            thesis="Fundamentals solid. News is positive.", sentiment_evidence=[], fundamental_evidence=[],
            quantitative_evidence={}, provider_id="MockAI", confidence=0.85, risks=["Market volatility"]
        )
        
        opp = signal_engine.create_opportunity(
            symbol=unique_symbol, timestamp=datetime.now(timezone.utc), decision_mode=DecisionMode.HYBRID,
            strategy_signal=strategy_sig, ai_analysis=ai_analysis
        )
        opp.suggested_position_size = 5.0
        
        print(f"SUCCESS: Created Opportunity {opp.opportunity_id}")
        
        # 5. Push to Workflow (Risk Gate -> User Decision -> Paper Execution)
        print("\n--- Processing Workflow ---")
        current_price = 2800.0 # Mocked price for execution
        await orchestrator.process_new_opportunity(opp, current_price, db)
        
        print("Approving opportunity (TAKE_TRADE)...")
        order = await orchestrator.process_user_action(opp, "TAKE_TRADE", current_price, db)
        print(f"SUCCESS: Order executed. Order ID: {order.order_id}")
        
        # 6. Verify Portfolio
        portfolio = get_portfolio()
        positions = portfolio.get_positions()
        print(f"\n--- Portfolio Summary ---")
        print(f"Total Value: {portfolio.get_summary({unique_symbol: current_price}).total_value}")
        print(f"Positions: {len(positions)}")
        for pos in positions:
            print(f"  {pos.instrument_id}: {pos.quantity} shares")
            
        print("\nE2E VALIDATION PASS.")
        
    except Exception as e:
        print(f"\nE2E VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
