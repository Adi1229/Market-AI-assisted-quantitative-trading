import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.data.database.session import SessionLocal, engine, Base
from app.engine.workflow import WorkflowOrchestrator
from app.engine.risk import RiskEngine
from app.engine.portfolio import VirtualPortfolio
from app.engine.execution import PaperExecutionProvider
from app.engine.notification import NotificationAdapter
from app.engine.models import TradeOpportunity, DecisionMode
from app.operations.incidents import incident_manager
from app.operations.health import health_monitor

class MockNotificationAdapter(NotificationAdapter):
    async def send_opportunity(self, opp): pass
    async def send_execution_result(self, order): pass
    async def send_daily_summary(self, session_id): pass

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    
@pytest.mark.asyncio
async def test_e2e_operations_isolation(db):
    """
    Simulates a full paper operations lifecycle containing artificial errors.
    Ensures that the state machine catches everything and the application does not crash.
    """
    portfolio = VirtualPortfolio(initial_capital=100000.0)
    portfolio.load_from_db(db)
    
    execution = PaperExecutionProvider(portfolio)
    risk_engine = RiskEngine()
    notification = MockNotificationAdapter()
    
    orchestrator = WorkflowOrchestrator(
        risk_engine=risk_engine,
        execution_provider=execution,
        notification_adapter=notification
    )
    
    from app.engine.models import Direction
    
    # 1. Healthy trade
    opp1 = TradeOpportunity(
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
    
    await orchestrator.process_new_opportunity(opp1, 2500.0, db)
    await orchestrator.process_user_action(opp1, "TAKE_TRADE", 2500.0, db)
    
    assert opp1.status.value == "EXECUTED"
    
    # 2. Simulate Provider 429
    health_monitor.record_provider_error(db, "upstox", "429", "Simulated Rate Limit")
    health_monitor.record_provider_error(db, "upstox", "429", "Simulated Rate Limit")
    health_monitor.record_provider_error(db, "upstox", "429", "Simulated Rate Limit")
    
    incidents = incident_manager.get_active_incidents(db)
    assert any(i.category == "PROVIDER_429" for i in incidents)
    
    # 3. Simulate Stale Data (Gaps)
    stale_time = datetime.now(timezone.utc) - timedelta(minutes=20)
    health_monitor.update_market_health(db, "^NSEI", "mock", "5m", stale_time, stale_time)
    
    # 4. Simulate Crash in Risk (if someone modified it)
    # We will pass an invalid type to force a python exception
    class BadOpp:
        def __init__(self):
            self.timestamp = "Not a datetime"
            self.opportunity_id = "test_bad"
            self.symbol = "BAD"
            self.status = opp1.status # valid status to pass early check
            self.decision_mode = opp1.decision_mode
            self.direction = 1
            self.confidence_score = 0
            self.strategy_version = "1"
            self.ai_confidence = 0
            self.hybrid_score = 0
            self.market_regime = ""
            self.strategy_evidence = None
            self.ai_evidence = None
            self.reasoning = []
            
    bad_opp = BadOpp()
    
    with pytest.raises(Exception):
        await orchestrator.process_new_opportunity(bad_opp, 100, db)
        
    incidents_after = incident_manager.get_active_incidents(db)
    assert any(i.category == "WORKFLOW_ERROR" for i in incidents_after)
    
    print("E2E operations failure isolation successful.")
