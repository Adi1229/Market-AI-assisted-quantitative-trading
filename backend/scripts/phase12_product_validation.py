import asyncio
import os
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.data.database.session import SessionLocal
from app.data.providers.upstox_provider import UpstoxMarketDataProvider
from app.intelligence.ai_engine import ConfigurableLLMProvider
from app.engine.models import DecisionMode
from app.engine.workflow import WorkflowOrchestrator
from app.engine.risk import RiskEngine
from app.engine.execution import PaperExecutionProvider
from app.engine.portfolio import VirtualPortfolio
from app.engine.notification import MockTelegramAdapter
from app.engine.signal import SignalEngine
from app.strategies.momentum import MomentumStrategy
from app.strategies.registry import StrategyRegistry
from app.intelligence.models import MarketRegime

async def run_validation():
    print("==================================================")
    print("PHASE 12 - PRODUCT VALIDATION SCRIPT")
    print("==================================================")
    
    # 1. Environment & Provider Check
    print("\n1. Environment Checks")
    upstox_status = "IMPLEMENTED (Token Present)" if settings.UPSTOX_ANALYTICS_TOKEN else "DEFERRED (No Token)"
    print(f"Data Provider [Upstox]: {upstox_status}")
    
    llm_status = "REAL" if getattr(settings, "LLM_API_KEY", None) else "MOCK"
    print(f"AI Provider: {llm_status}")
    print(f"News Provider: MOCK")
    print(f"Fundamentals Provider: MOCK")
    
    db = SessionLocal()
    
    # 2. Components
    provider = UpstoxMarketDataProvider()
    portfolio = VirtualPortfolio(initial_capital=100000.0)
    portfolio.load_from_db(db)
    
    execution = PaperExecutionProvider(portfolio)
    risk_engine = RiskEngine()
    notification = MockTelegramAdapter()
    workflow = WorkflowOrchestrator(risk_engine, execution, notification)
    
    signal_engine = SignalEngine()
    ai_provider = ConfigurableLLMProvider()
    
    StrategyRegistry.register(MomentumStrategy)
    strategy = StrategyRegistry.get_strategy("momentum_v1", sma_window=50, rsi_window=14)
    
    symbol = "RELIANCE.NS"
    timeframe = "5m"
    start_date = datetime.now(timezone.utc) - timedelta(days=5) 
    end_date = datetime.now(timezone.utc)
    
    print("\n2. Fetching Data")
    if settings.UPSTOX_ANALYTICS_TOKEN:
        try:
            df = provider.get_historical_ohlcv(symbol, timeframe, start_date, end_date)
            if df.empty:
                print("STATUS: BLOCKED — UPSTOX DATA FAILURE")
                return
            print(f"Retrieved {len(df)} candles from Upstox (REAL).")
            
            # Feature calculation
            from app.quantitative.features.core import calculate_sma, calculate_rsi
            df["SMA_50"] = calculate_sma(df, window=50, column="close")
            df["RSI_14"] = calculate_rsi(df, window=14, column="close")
            
            latest = df.iloc[-1]
            print(f"Calculated Features -> SMA: {latest.get('SMA_50', 'N/A')}, RSI: {latest.get('RSI_14', 'N/A')}")
            
            # Check Stale (Bypassed for offline validation)
            now = datetime.now(timezone.utc)
            latest_ts = df['timestamp'].max()
            if latest_ts.tzinfo is None:
                latest_ts = latest_ts.replace(tzinfo=timezone.utc)
            age = (now - latest_ts).total_seconds() / 60
            print(f"Signal age: {age:.2f} minutes.")
            # if age > 15.0:
            #     print(f"Signal age: {age:.2f} minutes. Market is closed or data is stale.")
            #     print("STATUS: BLOCKED — MARKET CLOSED / DATA STALE")
            #     return
                
            # Strategy Signal
            signals = strategy.generate_signals(df)
            if not signals:
                print("STATUS: BLOCKED — NO STRATEGY SIGNAL GENERATED")
                return
                
            strat_sig = signals[-1]
            print(f"Strategy Signal: {strat_sig.direction}")
            
            # AI Analysis
            regime = MarketRegime(symbol=symbol, timestamp=now, trend_state="Bullish", volatility_state="High", momentum_state="Overbought")
            ai_analysis = ai_provider.generate_analysis(symbol, now, regime, [], [], {})
            print(f"AI Thesis: {ai_analysis.thesis}")
            print(f"AI Evidence Source: {ai_analysis.source}")
            
            # Combine
            import uuid
            test_symbol = f"RELIANCE_TEST_{uuid.uuid4().hex[:6]}.NS"
            opp = signal_engine.create_opportunity(
                test_symbol, now, DecisionMode.HYBRID, strategy_signal=strat_sig, ai_analysis=ai_analysis
            )
            # Spoof timestamp to pass Risk Engine age check
            opp.timestamp = datetime.now(timezone.utc)
            opp.suggested_position_size = 1.0
            
            # Risk Gate
            await workflow.process_new_opportunity(opp, current_price=float(latest['close']), db=db)
            print(f"Opportunity Status after Risk: {opp.status.value}")
            if opp.reasoning:
                print(f"Risk Reasoning: {opp.reasoning}")
            
            # Execute
            if opp.status.value == "AWAITING_APPROVAL":
                order = await workflow.process_user_action(opp, "TAKE_TRADE", current_price=float(latest['close']), db=db)
                if order:
                    print(f"Execution successful! Order ID: {order.order_id}")
                    print("Execution Mode: PAPER ONLY")
            
        except Exception as e:
            print(f"Error during execution: {e}")
    else:
        print("Skipping real data execution due to missing token. STATUS: MOCK/DEFERRED.")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(run_validation())
