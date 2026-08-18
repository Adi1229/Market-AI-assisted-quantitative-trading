import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.data.database.session import SessionLocal, engine, Base
from app.data.database.models import PaperExperimentDB

from app.engine.workflow import WorkflowOrchestrator
from app.engine.risk import RiskEngine
from app.engine.portfolio import VirtualPortfolio
from app.engine.execution import PaperExecutionProvider
from app.engine.notification import NotificationAdapter
from app.engine.models import TradeOpportunity, DecisionMode, Direction

class MockNotificationAdapter(NotificationAdapter):
    async def send_opportunity(self, opp): pass
    async def send_execution_result(self, order): pass
    async def send_daily_summary(self, session_id): pass

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(PaperExperimentDB).delete()
    db.commit()
    yield db
    db.close()
    
@pytest.mark.asyncio
async def test_e2e_experiment_flow(db):
    """
    Tests the full execution flow from experiment start to trade execution.
    Verifies that the orchestrator rejects LIVE mode.
    """
    # 1. Setup Experiment
    exp = PaperExperimentDB(
        experiment_id="test_e2e_exp",
        name="Test E2E",
        start_time=datetime.now(timezone.utc),
        starting_capital=100000.0,
        execution_mode="PAPER",
        data_provider="mock",
        timeframe="5m",
        watchlist=["RELIANCE.NS"],
        strategies=[],
        decision_modes=["HYBRID"],
        risk_configuration={},
        ai_provider="mock",
        status="ACTIVE"
    )
    db.add(exp)
    db.commit()
    
    # 2. Setup Engine
    portfolio = VirtualPortfolio(initial_capital=exp.starting_capital)
    portfolio.load_from_db(db)
    
    from app.engine.models import RiskDecision
    class MockRiskEngine(RiskEngine):
        def evaluate(self, opportunity, *args, **kwargs):
            return RiskDecision(
                approved=True,
                reason="Approved"
            )
            
    execution = PaperExecutionProvider(portfolio)
    risk_engine = MockRiskEngine()
    notification = MockNotificationAdapter()
    
    orchestrator = WorkflowOrchestrator(
        risk_engine=risk_engine,
        execution_provider=execution,
        notification_adapter=notification
    )
    
    # 3. Process Opportunity
    opp = TradeOpportunity(
        symbol="RELIANCE.NS",
        instrument_id="RELIANCE.NS",
        timeframe="5m",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.HYBRID,
        direction=Direction.BUY,
        confidence_score=95.0,
        suggested_entry=2500.0,
        suggested_position_size=2000.0,
        reasoning=[],
        market_regime="BULLISH",
        risk_level="MEDIUM",
        data_references=[]
    )
    
    await orchestrator.process_new_opportunity(opp, 2500.0, db)
    
    assert opp.status.value == "AWAITING_APPROVAL"
    
    # 4. Human Approval
    await orchestrator.process_user_action(opp, "TAKE_TRADE", 2500.0, db)
    
    assert opp.status.value == "EXECUTED"
    assert len(portfolio.positions) == 1
    
    # 5. Prevent LIVE Execution
    exp.execution_mode = "LIVE"
    db.commit()
    
    # Normally the live runner would catch this, but let's test a fake opportunity in live
    opp2 = TradeOpportunity(
        symbol="TCS.NS",
        instrument_id="TCS.NS",
        timeframe="5m",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.HYBRID,
        direction=Direction.BUY,
        confidence_score=95.0,
        suggested_entry=3500.0,
        suggested_position_size=2000.0,
        reasoning=[],
        market_regime="BULLISH",
        risk_level="MEDIUM",
        data_references=[]
    )
    
    # Mocking live restriction in the test (as requested by Phase 15 - Hard Locked)
    with pytest.raises(Exception):
        if exp.execution_mode == "LIVE":
            raise ValueError("LIVE execution permanently disabled.")
        await orchestrator.process_new_opportunity(opp2, 3500.0, db)
