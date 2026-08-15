import pytest
import asyncio
from datetime import datetime, timedelta

from app.engine.models import (
    TradeOpportunity, DecisionMode, Direction, OpportunityStatus,
    StrategyEvidence, AIEvidence
)
from app.engine.signal import SignalEngine
from app.engine.risk import RiskEngine
from app.engine.execution import PaperExecutionProvider
from app.engine.portfolio import VirtualPortfolio
from app.engine.notification import MockTelegramAdapter
from app.engine.workflow import WorkflowOrchestrator
from app.strategies.base import StrategySignal
from app.intelligence.models import AIAnalysis

@pytest.fixture
def orchestrator():
    risk = RiskEngine()
    risk.max_position_size = 1000.0
    portfolio = VirtualPortfolio(initial_capital=10000.0)
    execution = PaperExecutionProvider(portfolio)
    notification = MockTelegramAdapter()
    return WorkflowOrchestrator(risk, execution, notification)

@pytest.fixture
def signal_engine():
    return SignalEngine()

def test_signal_engine_hybrid_mode(signal_engine):
    """Test Hybrid Decision Aggregation."""
    strategy_sig = StrategySignal(symbol="TEST", strategy_id="mock", strategy_version="1", direction=1, features={}, timestamp=datetime.now())
    ai_analysis = AIAnalysis(
        symbol="TEST", timestamp=datetime.now(), market_context="Bullish",
        thesis="Look good", sentiment_evidence=[], fundamental_evidence=[],
        quantitative_evidence={}, provider_id="MockAI", confidence=0.8, risks=[]
    )
    
    opp = signal_engine.create_opportunity(
        symbol="TEST",
        timestamp=datetime.now(),
        decision_mode=DecisionMode.HYBRID,
        strategy_signal=strategy_sig,
        ai_analysis=ai_analysis
    )
    
    assert opp.decision_mode == DecisionMode.HYBRID
    assert opp.direction == Direction.BUY
    assert opp.strategy_evidence is not None
    assert opp.ai_evidence is not None
    
    # 80 * 0.5 + 80 * 0.5 = 80. + 10 agreement bonus = 90
    assert opp.confidence_score == 90.0
    assert opp.status == OpportunityStatus.CREATED

def test_workflow_risk_rejection(orchestrator):
    """Test Risk Engine hard gate."""
    opp = TradeOpportunity(
        symbol="TEST", instrument_id="TEST", timestamp=datetime.now(),
        decision_mode=DecisionMode.STRATEGY_ONLY, direction=Direction.BUY,
        confidence_score=90.0, risk_level="LOW", reasoning=[], data_references=[],
        suggested_position_size=5000.0, market_regime="Unknown"
    )
    
    asyncio.run(orchestrator.process_new_opportunity(opp, current_price=100.0))
    assert opp.status == OpportunityStatus.RISK_REJECTED
    assert any("MAX_POSITION_SIZE_EXCEEDED" in r for r in opp.reasoning)

def test_workflow_stale_signal(orchestrator):
    """Test stale signal rejection."""
    opp = TradeOpportunity(
        symbol="TEST", instrument_id="TEST", timestamp=datetime.now() - timedelta(minutes=10),
        decision_mode=DecisionMode.STRATEGY_ONLY, direction=Direction.BUY,
        confidence_score=90.0, risk_level="LOW", reasoning=[], data_references=[],
        suggested_position_size=100.0, market_regime="Unknown"
    )
    asyncio.run(orchestrator.process_new_opportunity(opp, current_price=100.0))
    assert opp.status == OpportunityStatus.RISK_REJECTED
    assert any("STALE_SIGNAL" in r for r in opp.reasoning)

def test_workflow_execution_and_idempotency(orchestrator):
    """Test approval workflow, paper execution, and idempotency."""
    opp = TradeOpportunity(
        symbol="TEST", instrument_id="TEST", timestamp=datetime.now(),
        decision_mode=DecisionMode.STRATEGY_ONLY, direction=Direction.BUY,
        confidence_score=90.0, risk_level="LOW", reasoning=[], data_references=[],
        suggested_position_size=10.0, market_regime="Unknown"
    )
    
    asyncio.run(orchestrator.process_new_opportunity(opp, current_price=100.0))
    assert opp.status == OpportunityStatus.AWAITING_APPROVAL
    
    # User clicks TAKE_TRADE
    order = asyncio.run(orchestrator.process_user_action(opp, "TAKE_TRADE", current_price=100.0))
    
    assert order is not None
    assert opp.status == OpportunityStatus.EXECUTED
    assert order.fill_price > 100.0 # Slippage added
    
    portfolio = asyncio.run(orchestrator.execution.get_portfolio_summary({"TEST": 100.0}))
    assert portfolio.open_positions == 1
    assert portfolio.cash < 10000.0 # Deducted cost basis + commission
    
    # Try TAKE_TRADE again to verify idempotency
    order2 = asyncio.run(orchestrator.process_user_action(opp, "TAKE_TRADE", current_price=100.0))
    assert order2 is None # Idempotency blocked it
    
    # Double check portfolio hasn't changed
    portfolio2 = asyncio.run(orchestrator.execution.get_portfolio_summary({"TEST": 100.0}))
    assert portfolio2.open_positions == 1

def test_workflow_live_safety_block(orchestrator):
    """Test that LIVE execution is blocked by default."""
    orchestrator.execution = type('MockExecution', (), {'execution_mode': 'LIVE', 'get_portfolio_summary': orchestrator.execution.get_portfolio_summary, 'get_positions': orchestrator.execution.get_positions})()
    
    opp = TradeOpportunity(
        symbol="TEST", instrument_id="TEST", timestamp=datetime.now(),
        decision_mode=DecisionMode.STRATEGY_ONLY, direction=Direction.BUY,
        confidence_score=90.0, risk_level="LOW", reasoning=[], data_references=[],
        suggested_position_size=10.0, market_regime="Unknown"
    )
    
    asyncio.run(orchestrator.process_new_opportunity(opp, current_price=100.0))
    
    try:
        asyncio.run(orchestrator.process_user_action(opp, "TAKE_TRADE", current_price=100.0))
    except RuntimeError as e:
        assert "LIVE execution mode disabled" in str(e)
        
    assert opp.status == OpportunityStatus.EXECUTION_FAILED
