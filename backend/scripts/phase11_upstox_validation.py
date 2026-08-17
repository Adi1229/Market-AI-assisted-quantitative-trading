import sys
import asyncio
from datetime import datetime, timedelta, timezone
from pprint import pprint
import pandas as pd

# Setup paths
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.data.database.session import SessionLocal
from app.data.providers.upstox_provider import UpstoxMarketDataProvider
from app.data.ingestion import DataIngestionService
from app.engine.signal import SignalEngine
from app.engine.risk import RiskEngine
from app.engine.portfolio import VirtualPortfolio
from app.engine.execution import PaperExecutionProvider
from app.engine.notification import MockTelegramAdapter
from app.engine.workflow import WorkflowOrchestrator
from app.strategies.registry import StrategyRegistry
from app.strategies.momentum.strategy import MomentumStrategy
from app.intelligence.ai_provider import MockAIProvider
from app.engine.models import DecisionMode, OpportunityStatus

async def run_experiment():
    print("==================================================")
    print("PHASE 11A — UPSTOX REAL MARKET DATA & PAPER-TRADING VALIDATION")
    print("==================================================")
    
    if not settings.UPSTOX_ANALYTICS_TOKEN:
        print("\nBLOCKED — UPSTOX ANALYTICS TOKEN UNAVAILABLE")
        print("Please configure UPSTOX_ANALYTICS_TOKEN in backend/.env to run this validation.")
        return
        
    print("Credentials Found (Safe Check Passed)")
    
    # 1. Initialize components
    db = SessionLocal()
    
    # Use real Upstox provider
    provider = UpstoxMarketDataProvider()
    ingestion = DataIngestionService(provider, db)
    
    portfolio = VirtualPortfolio(initial_capital=100000.0)
    portfolio.load_from_db(db)
    
    execution = PaperExecutionProvider(portfolio)
    risk_engine = RiskEngine()
    notification = MockTelegramAdapter()
    workflow = WorkflowOrchestrator(risk_engine, execution, notification)
    
    ai_provider = MockAIProvider()
    signal_engine = SignalEngine()
    
    # Register strategy
    StrategyRegistry.register(MomentumStrategy)
    strategy = StrategyRegistry.get_strategy("momentum_v1", sma_window=50, rsi_window=14)
    
    symbol = "RELIANCE.NS"
    timeframe = "1d"
    start_date = datetime.now(timezone.utc) - timedelta(days=90)
    end_date = datetime.now(timezone.utc)
    
    stats = {
        "signals_generated": 0,
        "risk_rejected": 0,
        "approved_by_user": 0,
        "executed": 0,
        "duplicate_blocks": 0
    }
    
    print(f"\n1. Ingesting Real Data for {symbol} ({timeframe}) from Upstox")
    try:
        inserted = ingestion.ingest_historical_data(symbol, timeframe, start_date, end_date)
        print(f"Data Ingested: {inserted} rows")
    except Exception as e:
        print(f"Ingestion Failed: {e}")
        db.close()
        return
        
    print(f"\n2. Fetching Data for Signal Generation")
    df = provider.get_historical_ohlcv(symbol, timeframe, start_date, end_date)
    
    if df.empty:
        print("Dataframe is empty, cannot proceed.")
        db.close()
        return
        
    print(f"Provider: Upstox")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Rows: {len(df)}")
    print(f"First timestamp: {df['timestamp'].min()}")
    print(f"Last timestamp: {df['timestamp'].max()}")
    print(f"First close: {df.iloc[0]['close']}")
    print(f"Last close: {df.iloc[-1]['close']}")
        
    # Compute features
    import app.quantitative.features.core as features
    df['SMA_50'] = features.calculate_sma(df, 50)
    df['RSI_14'] = features.calculate_rsi(df, 14)
    df = df.dropna()
    
    print(f"\n3. Generating Strategy Signals")
    
    if df.empty:
        print("NO SIGNAL")
        print("Not enough data for moving averages and RSI.")
        db.close()
        return
        
    signals = strategy.generate_signals(df)
    print(f"Generated {len(signals)} raw strategy signals.")
    
    if not signals:
        print("NO SIGNAL")
        db.close()
        return
        
    latest_signal = signals[-1]
    stats["signals_generated"] += 1
    from app.intelligence.ai_engine import MockAIProvider as EngineMockAIProvider
    from app.intelligence.models import MarketRegime
    engine_ai_provider = EngineMockAIProvider()
    
    print(f"\n4. Passing to Signal Engine (HYBRID Mode)")
    print("AI SOURCE: MOCK / SIMULATED")
    
    ai_analysis = engine_ai_provider.generate_analysis(
        symbol=symbol,
        timestamp=pd.Timestamp(latest_signal.timestamp).to_pydatetime().replace(tzinfo=timezone.utc) if latest_signal.timestamp else datetime.now(timezone.utc),
        regime=MarketRegime(symbol=symbol, timestamp=datetime.now(timezone.utc), trend_state="Bullish", volatility_state="Normal", momentum_state="High"),
        sentiment_evidence=[],
        fundamental_evidence=[],
        quantitative_evidence={"momentum": latest_signal.direction}
    )
    
    opportunity = signal_engine.create_opportunity(
        symbol=symbol,
        timestamp=pd.Timestamp(latest_signal.timestamp).to_pydatetime().replace(tzinfo=timezone.utc) if latest_signal.timestamp else datetime.now(timezone.utc),
        decision_mode=DecisionMode.HYBRID,
        strategy_signal=latest_signal,
        ai_analysis=ai_analysis
    )
    
    print(f"\n5. Processing Opportunity through Workflow")
    current_price = float(df.iloc[-1]['close'])
    
    await workflow.process_new_opportunity(opportunity, current_price, db)
    
    if opportunity.status == OpportunityStatus.RISK_REJECTED:
        stats["risk_rejected"] += 1
        print("Opportunity Rejected by Risk Engine:")
        print(opportunity.reasoning)
    elif opportunity.status == OpportunityStatus.AWAITING_APPROVAL:
        print("Opportunity Passed Risk. Awaiting Approval.")
        
        # Simulate User Clicking "TAKE PAPER TRADE"
        print("\n6. Simulating Human Approval (TAKE_TRADE)")
        order = await workflow.process_user_action(opportunity, "TAKE_TRADE", current_price, db)
        
        if order:
            print("Order Executed Successfully!")
            stats["approved_by_user"] += 1
            stats["executed"] += 1
            
            # Simulate duplicate attempt
            print("\n7. Simulating Duplicate TAKE_TRADE Attempt")
            duplicate_order = await workflow.process_user_action(opportunity, "TAKE_TRADE", current_price, db)
            if not duplicate_order:
                print("Duplicate Blocked via Idempotency")
                stats["duplicate_blocks"] += 1
        else:
            print("Order Execution Failed.")
    
    print("\n==================================================")
    print("EXPERIMENT RESULTS")
    print("==================================================")
    print(f"Total Portfolio Value: {portfolio.cash + sum([p.quantity * current_price for p in portfolio.positions])}")
    print(f"Realized P&L: {portfolio.realized_pnl}")
    pprint(stats)
    
    db.close()

if __name__ == "__main__":
    asyncio.run(run_experiment())
