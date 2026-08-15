import asyncio
from datetime import datetime
from app.engine.models import DecisionMode
from app.engine.signal import SignalEngine
from app.engine.risk import RiskEngine
from app.engine.execution import PaperExecutionProvider
from app.engine.portfolio import VirtualPortfolio
from app.engine.notification import MockTelegramAdapter
from app.engine.workflow import WorkflowOrchestrator

from app.strategies.base import StrategySignal
from app.intelligence.models import AIAnalysis

async def run_e2e():
    print("=== STARTING PHASE 5 E2E VERIFICATION ===\n")
    
    # 1. Initialize Components
    signal_engine = SignalEngine()
    risk = RiskEngine()
    portfolio = VirtualPortfolio(initial_capital=100000.0)
    execution = PaperExecutionProvider(portfolio)
    notification = MockTelegramAdapter()
    orchestrator = WorkflowOrchestrator(risk, execution, notification)
    
    # 2. Mock Signals
    strategy_sig = StrategySignal(symbol="RELIANCE", strategy_id="mock", strategy_version="1", direction=1, features={}, timestamp=datetime.now())
    ai_analysis = AIAnalysis(
        symbol="RELIANCE", timestamp=datetime.now(), market_context="Bullish",
        thesis="Strong fundamentals and trend.", sentiment_evidence=[], fundamental_evidence=[],
        quantitative_evidence={}, provider_id="MockAI", confidence=0.85, risks=[]
    )
    
    current_market_price = 2450.0
    
    # --- SCENARIO 1: STRATEGY ONLY ---
    print("\n--- SCENARIO 1: STRATEGY ONLY ---")
    opp1 = signal_engine.create_opportunity(
        symbol="RELIANCE", timestamp=datetime.now(), decision_mode=DecisionMode.STRATEGY_ONLY,
        strategy_signal=strategy_sig
    )
    opp1.suggested_position_size = 10.0 # Buy 10 shares
    
    print(f"Generated Opportunity: {opp1.opportunity_id} - Score: {opp1.confidence_score}")
    await orchestrator.process_new_opportunity(opp1, current_price=current_market_price)
    
    print("\nSimulating User Clicking TAKE_TRADE...")
    await orchestrator.process_user_action(opp1, "TAKE_TRADE", current_market_price)
    
    summary = await execution.get_portfolio_summary({"RELIANCE": 2450.0})
    print(f"Portfolio Value: {summary.total_value}, Cash: {summary.cash}, Positions: {summary.open_positions}")
    
    
    # --- SCENARIO 2: AI ONLY ---
    print("\n--- SCENARIO 2: AI ONLY ---")
    opp2 = signal_engine.create_opportunity(
        symbol="HDFC", timestamp=datetime.now(), decision_mode=DecisionMode.AI_ONLY,
        ai_analysis=ai_analysis
    )
    opp2.suggested_position_size = 5.0 
    
    print(f"Generated Opportunity: {opp2.opportunity_id} - Score: {opp2.confidence_score}")
    await orchestrator.process_new_opportunity(opp2, current_price=1500.0)
    
    print("\nSimulating User Clicking IGNORE...")
    await orchestrator.process_user_action(opp2, "IGNORE", 1500.0)
    print(f"Opportunity Status: {opp2.status}")
    
    
    # --- SCENARIO 3: HYBRID ---
    print("\n--- SCENARIO 3: HYBRID ---")
    opp3 = signal_engine.create_opportunity(
        symbol="INFY", timestamp=datetime.now(), decision_mode=DecisionMode.HYBRID,
        strategy_signal=strategy_sig, ai_analysis=ai_analysis
    )
    opp3.suggested_position_size = 20.0 
    
    print(f"Generated Opportunity: {opp3.opportunity_id} - Score: {opp3.confidence_score}")
    await orchestrator.process_new_opportunity(opp3, current_price=1400.0)
    
    print("\nSimulating User Clicking TAKE_TRADE...")
    await orchestrator.process_user_action(opp3, "TAKE_TRADE", 1400.0)
    
    summary = await execution.get_portfolio_summary({"RELIANCE": 2450.0, "INFY": 1400.0})
    print(f"Portfolio Value: {summary.total_value}, Cash: {summary.cash}, Positions: {summary.open_positions}")
    
    print("\n=== E2E VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(run_e2e())
