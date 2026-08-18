import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.data.database.session import SessionLocal, engine, Base
from app.operations.health import health_monitor
from app.operations.incidents import incident_manager
from app.operations.reconciliation import reconciliation_service
from app.data.database.models import IncidentDB, ProviderHealthDB, MarketHealthDB, PortfolioStateDB, PositionDB

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Clean tables
    db.query(IncidentDB).delete()
    db.query(ProviderHealthDB).delete()
    db.query(MarketHealthDB).delete()
    db.query(PortfolioStateDB).delete()
    db.query(PositionDB).delete()
    db.commit()
    try:
        yield db
    finally:
        db.close()
        
def test_provider_health_logging(db):
    health_monitor.record_provider_error(db, "upstox", "429", "Rate Limit")
    ph = db.query(ProviderHealthDB).filter_by(provider_id="upstox").first()
    assert ph.error_429_count == 1
    assert ph.consecutive_failures == 1
    assert ph.status == "HEALTHY" # Need 3 for error
    
    health_monitor.record_provider_error(db, "upstox", "TIMEOUT", "Timed out")
    health_monitor.record_provider_error(db, "upstox", "TIMEOUT", "Timed out again")
    
    ph = db.query(ProviderHealthDB).filter_by(provider_id="upstox").first()
    assert ph.timeout_count == 2
    assert ph.consecutive_failures == 3
    assert ph.status == "ERROR"
    
    # Check incidents
    incidents = incident_manager.get_active_incidents(db)
    assert len(incidents) == 3
    assert incidents[0].severity == "ERROR" # The 3rd failure logged as ERROR

def test_market_health_staleness(db):
    now = datetime.now(timezone.utc)
    stale_time = now - timedelta(minutes=15)
    
    # We are passing the time into update_market_health which calculates age.
    # Assuming the market is open (or using a mock time to simulate market open).
    # Since HealthMonitor checks actual time for market open, it might be closed during testing.
    # We will test the age calculation explicitly.
    health_monitor.update_market_health(db, "RELIANCE.NS", "upstox", "5m", stale_time, stale_time)
    
    mh = db.query(MarketHealthDB).filter_by(symbol="RELIANCE.NS").first()
    assert mh.data_age_seconds >= 900
    
def test_reconciliation_error(db):
    from app.engine.portfolio import VirtualPortfolio
    
    # Fake mismatch
    state = PortfolioStateDB(id="virtual", cash=120000.0, realized_pnl=0.0)
    db.add(state)
    db.commit()
    
    portfolio = VirtualPortfolio(initial_capital=100000.0) # memory is 100k
    reconciliation_service.reconcile_portfolio(db, portfolio)
    
    incidents = incident_manager.get_active_incidents(db)
    crit_incidents = [i for i in incidents if i.severity == "CRITICAL" and i.category == "RECONCILIATION_ERROR"]
    assert len(crit_incidents) >= 1
    
@pytest.mark.asyncio
async def test_workflow_error_isolation(db):
    from app.engine.workflow import WorkflowOrchestrator
    from app.engine.risk import RiskEngine
    from app.engine.execution import PaperExecutionProvider
    from app.engine.portfolio import VirtualPortfolio
    
    class FailingRiskEngine(RiskEngine):
        def evaluate(self, *args, **kwargs):
            raise RuntimeError("Fake unexpected failure")
            
    orchestrator = WorkflowOrchestrator(
        risk_engine=FailingRiskEngine(),
        execution_provider=PaperExecutionProvider(VirtualPortfolio()),
        notification_adapter=None
    )
    
    from app.engine.models import TradeOpportunity, DecisionMode, Direction
    
    opp = TradeOpportunity(
        symbol="RELIANCE.NS",
        instrument_id="RELIANCE.NS",
        timeframe="5m",
        timestamp=datetime.now(timezone.utc),
        decision_mode=DecisionMode.STRATEGY_ONLY,
        direction=Direction.BUY,
        confidence_score=90.0,
        reasoning=[],
        market_regime="BULLISH",
        risk_level="MEDIUM",
        data_references=[]
    )
    
    # Process should raise but log incident
    with pytest.raises(RuntimeError):
        await orchestrator.process_new_opportunity(opp, 100.0, db)
        
    incidents = incident_manager.get_active_incidents(db)
    assert len(incidents) > 0
    assert incidents[0].category == "WORKFLOW_ERROR"
