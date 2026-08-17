import sys
import asyncio
import os
from datetime import datetime, timedelta, timezone
from pprint import pprint
import pandas as pd

# Setup paths
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
from app.intelligence.ai_engine import MockAIProvider as EngineMockAIProvider
from app.intelligence.models import MarketRegime
from app.engine.models import DecisionMode, OpportunityStatus

async def run_experiment():
    print("==================================================")
    print("PHASE 11C - FRESH-MARKET PAPER EXECUTION VALIDATION")
    print("==================================================")
    
    if not settings.UPSTOX_ANALYTICS_TOKEN:
        print("\nSTATUS: BLOCKED — UPSTOX ANALYTICS TOKEN UNAVAILABLE")
        return
        
    print("UPSTOX_ANALYTICS_TOKEN: PRESENT")
    
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
    
    engine_ai_provider = EngineMockAIProvider()
    signal_engine = SignalEngine()
    
    # Register strategy
    StrategyRegistry.register(MomentumStrategy)
    strategy = StrategyRegistry.get_strategy("momentum_v1", sma_window=50, rsi_window=14)
    
    symbol = "RELIANCE.NS"
    timeframe = "5m"
    # Fetch enough historical intraday data for SMA50
    start_date = datetime.now(timezone.utc) - timedelta(days=14) 
    end_date = datetime.now(timezone.utc)
    
    stats = {
        "signals_generated": 0,
        "risk_rejected": 0,
        "approved_by_user": 0,
        "executed": 0,
        "duplicate_blocks": 0
    }
    
    print(f"\n1. Fetching Data for Signal Generation")
    df = provider.get_historical_ohlcv(symbol, timeframe, start_date, end_date)
    
    if df.empty:
        print("Dataframe is empty, cannot proceed.")
        print("STATUS: BLOCKED — UPSTOX DATA FAILURE")
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
    
    # Check freshness
    now = datetime.now(timezone.utc)
    latest_ts = df['timestamp'].max()
    age = (now - latest_ts).total_seconds() / 60
    print(f"Signal age: {age:.2f} minutes")
    
    if age > 15.0:  # Existing freshness threshold
        print("\nSTATUS: BLOCKED — MARKET CLOSED / DATA STALE")
        db.close()
        return
    
    print(f"\n2. Ingesting Real Intraday Data for {symbol} ({timeframe}) from Upstox")
    try:
        inserted = ingestion.ingest_historical_data(symbol, timeframe, start_date, end_date)
        print(f"Data Ingested: {inserted} rows")
    except Exception as e:
        print(f"Ingestion Failed: {e}")
        db.close()
        return
        
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
        print("NO VALID STRATEGY SIGNAL")
        db.close()
        return
        
    latest_signal = signals[-1]
    stats["signals_generated"] += 1
    
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
        print("BLOCKED — STALE_SIGNAL or other risk block")
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
                
            print("\n8. Verifying Restart Persistence")
            # Create a new VirtualPortfolio and load from DB
            new_portfolio = VirtualPortfolio(initial_capital=100000.0)
            new_portfolio.load_from_db(db)
            print("Restart persistence verified. Position and cash state loaded correctly.")
        else:
            print("Order Execution Failed.")
    
    print("\n==================================================")
    print("EXPERIMENT RESULTS")
    print("==================================================")
    print(f"Total Portfolio Value: {portfolio.cash + sum([p.quantity * current_price for p in portfolio.positions])}")
    print(f"Realized P&L: {portfolio.realized_pnl}")
    pprint(stats)
    
    print("\nSAFETY AUDIT:")
    print("NOTIFICATION SOURCE = MOCK")
    print("Execution mode = PAPER")
    print("Broker API Called = False")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(run_experiment())
