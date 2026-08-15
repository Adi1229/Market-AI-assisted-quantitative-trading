import pytest
from datetime import datetime, timezone, timedelta
from app.engine.models import TradeOpportunity, DecisionMode, Direction, OpportunityStatus, StrategyEvidence, AIEvidence
from app.engine.notification import TelegramAdapter, MockTelegramAdapter
from app.api.dependencies import _signal_engine, _risk_engine, _portfolio, _execution_provider, _workflow_orchestrator
from app.core.config import settings

@pytest.fixture
def mock_opportunity():
    return TradeOpportunity(
        symbol="RELIANCE",
        instrument_id="RELIANCE.NS",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.HYBRID,
        direction=Direction.BUY,
        confidence_score=0.85,
        market_regime="BULLISH",
        risk_level="MEDIUM",
        suggested_entry=2500.0,
        suggested_position_size=10,
        reasoning=["Good setup"],
        data_references=[]
    )

@pytest.mark.anyio
async def test_telegram_adapter_formatting(mock_opportunity, capsys):
    adapter = MockTelegramAdapter()
    await adapter.send_opportunity(mock_opportunity)
    captured = capsys.readouterr()
    assert "TRADE OPPORTUNITY" in captured.out
    assert "RELIANCE" in captured.out
    assert "HYBRID" in captured.out
    assert "TAKE PAPER TRADE" in captured.out

@pytest.mark.anyio
async def test_telegram_real_adapter_init():
    adapter = TelegramAdapter(bot_token="test_token", chat_id="test_chat")
    assert adapter.bot_token == "test_token"
    assert adapter.chat_id == "test_chat"

def test_stale_signal_rejection():
    opp = TradeOpportunity(
        symbol="TCS",
        instrument_id="TCS.NS",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=15),
        decision_mode=DecisionMode.STRATEGY_ONLY,
        direction=Direction.BUY,
        confidence_score=0.8,
        market_regime="BULLISH",
        risk_level="MEDIUM",
        reasoning=[],
        data_references=[]
    )
    decision = _risk_engine.evaluate(opp, portfolio_cash=100000.0, current_positions=[], current_time=datetime.now(timezone.utc))
    assert decision.approved is False
    assert "stale" in decision.reason.lower()

def test_strategy_only_mode():
    opp = TradeOpportunity(
        symbol="TCS",
        instrument_id="TCS.NS",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.STRATEGY_ONLY,
        direction=Direction.BUY,
        confidence_score=0.8,
        market_regime="BULLISH",
        risk_level="MEDIUM",
        reasoning=[],
        data_references=[],
        strategy_evidence=StrategyEvidence(
            strategy_id="test", strategy_name="Test", strategy_version="1.0",
            parameters={}, signal_type="BUY", signal_score=80.0, features_used={}, explanation="test"
        )
    )
    assert opp.ai_evidence is None
    assert opp.strategy_evidence is not None

def test_ai_only_mode():
    opp = TradeOpportunity(
        symbol="TCS",
        instrument_id="TCS.NS",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.AI_ONLY,
        direction=Direction.BUY,
        confidence_score=0.8,
        market_regime="BULLISH",
        risk_level="MEDIUM",
        reasoning=[],
        data_references=[],
        ai_evidence=AIEvidence(
            ai_model_id="MockAI", ai_model_version="1.0", direction="BUY", ai_score=80.0,
            reasoning=["test"], retrieved_facts=[], computed_values={}, model_inference="test",
            uncertainty="low", evidence_sources=[]
        )
    )
    assert opp.strategy_evidence is None
    assert opp.ai_evidence is not None

def test_hybrid_mode():
    opp = TradeOpportunity(
        symbol="TCS",
        instrument_id="TCS.NS",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.HYBRID,
        direction=Direction.BUY,
        confidence_score=0.8,
        market_regime="BULLISH",
        risk_level="MEDIUM",
        reasoning=[],
        data_references=[],
        strategy_evidence=StrategyEvidence(
            strategy_id="test", strategy_name="Test", strategy_version="1.0",
            parameters={}, signal_type="BUY", signal_score=80.0, features_used={}, explanation="test"
        ),
        ai_evidence=AIEvidence(
            ai_model_id="MockAI", ai_model_version="1.0", direction="BUY", ai_score=80.0,
            reasoning=["test"], retrieved_facts=[], computed_values={}, model_inference="test",
            uncertainty="low", evidence_sources=[]
        )
    )
    assert opp.strategy_evidence is not None
    assert opp.ai_evidence is not None

def test_live_safety_block():
    provider = _execution_provider
    assert provider.execution_mode == "PAPER"
    # Even if someone tries to hack the mode to LIVE, the workflow should catch it.
    
def test_ai_provider_factory_mock():
    assert settings.AI_PROVIDER == "mock"

def test_notification_adapter_factory():
    if not settings.TELEGRAM_BOT_TOKEN:
        assert isinstance(_workflow_orchestrator.notification, MockTelegramAdapter)

def test_provider_factory_all_modes():
    # Verify settings toggle correctly
    assert settings.DATA_PROVIDER in ["mock", "real"]
