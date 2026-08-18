import pytest
from datetime import datetime, timezone, timedelta
from app.analytics.service import AnalyticsService
from app.data.database.session import Base
from app.engine.portfolio import VirtualPortfolio
from app.engine.models import ExecutionOrder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_paper_session_lifecycle(test_db):
    analytics = AnalyticsService(test_db)
    
    # 1. Start session
    session = analytics.start_session("Test Ops Session")
    assert session.status == "ACTIVE"
    assert session.starting_capital == 100000.0
    
    # 2. Pause session
    paused = analytics.pause_session(session.id)
    assert paused.status == "PAUSED"
    
    # 3. Resume session
    resumed = analytics.resume_session(session.id)
    assert resumed.status == "ACTIVE"
    
    # 4. End session
    ended = analytics.end_session(session.id)
    assert ended.status == "COMPLETED"

def test_paper_operations_analytics(test_db):
    analytics = AnalyticsService(test_db)
    session = analytics.start_session("Analytics Test")
    
    # We will manually inject TradeOpportunity and PaperTradingJournal entries to test analytics
    from app.data.database.models import TradeOpportunityDB, PaperTradingJournalDB
    import uuid
    
    # 1. Trade Opportunity (Buy RELIANCE)
    opp1 = TradeOpportunityDB(
        opportunity_id=str(uuid.uuid4()),
        session_id=session.id,
        symbol="RELIANCE.NS",
        timestamp=datetime.now(timezone.utc),
        decision_mode="HYBRID",
        direction="BUY",
        confidence_score=85.0,
        strategy_version="v1.0",
        ai_confidence=90.0,
        hybrid_score=87.5,
        market_regime="BULL",
        status="EXECUTED"
    )
    test_db.add(opp1)
    
    # 2. Add journal entries representing completed trades
    j1 = PaperTradingJournalDB(
        id=str(uuid.uuid4()),
        session_id=session.id,
        opportunity_id=opp1.opportunity_id,
        symbol="RELIANCE.NS",
        direction="LONG",
        entry_price=100.0,
        exit_price=110.0,  # Won trade
        quantity=10,
        realized_pnl=100.0,  # 10 * 10
        strategy="MomentumStrategy",
        strategy_version="v1.0",
        decision_mode="HYBRID",
        ai_score=90.0,
        hybrid_score=87.5,
        regime="BULL",
        fees=1.0,
        slippage=0.0,
        data_source="MOCK",
        ai_source="MOCK / SIMULATED",
        entry_time=datetime.now(timezone.utc) - timedelta(hours=1),
        exit_time=datetime.now(timezone.utc)
    )
    test_db.add(j1)
    test_db.commit()
    
    # Strategy Analytics
    strat_perf = analytics.get_strategy_performance(session.id)
    assert len(strat_perf) == 1
    assert strat_perf[0]["strategy"] == "MomentumStrategy (vv1.0)"
    assert strat_perf[0]["trades"] == 1
    assert strat_perf[0]["wins"] == 1
    assert strat_perf[0]["win_rate"] == 1.0
    
    # Regime Analytics
    regime_perf = analytics.get_regime_performance(session.id)
    assert regime_perf[0]["regime"] == "BULL"
    assert regime_perf[0]["win_rate"] == 1.0
    
    # AI Effectiveness
    ai_eff = analytics.get_ai_effectiveness(session.id)
    # Since AI > 50 and PnL > 0, it should be correct
    assert ai_eff["accuracy"] == 1.0
    assert ai_eff["correct_predictions"] == 1
    
    # Daily Report
    report = analytics.get_daily_report()
    assert report["total_trades"] == 1
    assert report["message"] == "INSUFFICIENT SAMPLE SIZE"  # Only 1 trade
