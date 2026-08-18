import pytest
from datetime import datetime, timezone, timedelta
import uuid

from app.data.database.session import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.database.models import (
    PaperTradingSessionDB,
    TradeOpportunityDB,
    PaperTradingJournalDB,
    PortfolioStateDB
)
from app.analytics.service import AnalyticsService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Initialize virtual portfolio
    db.add(PortfolioStateDB(id="virtual", cash=100000.0, realized_pnl=0.0))
    db.commit()
    
    yield db
    db.close()

def test_session_lifecycle(db_session):
    analytics = AnalyticsService(db_session)
    
    # Start
    session = analytics.start_session("Test Session")
    assert session.status == "ACTIVE"
    assert session.starting_capital == 100000.0
    
    current = analytics.get_current_session()
    assert current is not None
    assert current.id == session.id
    
    # End
    analytics.end_session(session.id)
    assert session.status == "COMPLETED"
    
    current = analytics.get_current_session()
    assert current is None

def test_analytics_calculation(db_session):
    analytics = AnalyticsService(db_session)
    session = analytics.start_session("Test Analytics")
    
    now = datetime.now(timezone.utc)
    
    # Create test opportunities
    opp1 = TradeOpportunityDB(
        opportunity_id=str(uuid.uuid4()),
        session_id=session.id,
        symbol="AAPL",
        timestamp=now,
        decision_mode="HYBRID",
        direction="BUY",
        confidence_score=80.0,
        strategy_version="1.0",
        market_regime="Bullish",
        status="CLOSED"
    )
    opp2 = TradeOpportunityDB(
        opportunity_id=str(uuid.uuid4()),
        session_id=session.id,
        symbol="MSFT",
        timestamp=now,
        decision_mode="STRATEGY_ONLY",
        direction="SELL",
        confidence_score=60.0,
        strategy_version="1.0",
        market_regime="Bearish",
        status="RISK_REJECTED",
        reasoning=["Risk: INSUFFICIENT_CAPITAL"]
    )
    db_session.add(opp1)
    db_session.add(opp2)
    
    # Create test journal entry for opp1
    journal1 = PaperTradingJournalDB(
        id=str(uuid.uuid4()),
        session_id=session.id,
        opportunity_id=opp1.opportunity_id,
        symbol="AAPL",
        direction="LONG",
        entry_price=150.0,
        exit_price=160.0,
        quantity=10,
        realized_pnl=100.0,
        strategy="momentum_v1",
        strategy_version="1.0",
        ai_score=80,
        hybrid_score=80,
        regime="Bullish",
        entry_time=now,
        exit_time=now + timedelta(hours=1)
    )
    db_session.add(journal1)
    
    # Update portfolio to reflect the PNL
    port = db_session.query(PortfolioStateDB).first()
    port.cash += 100.0
    db_session.commit()
    
    analytics.end_session(session.id)
    
    metrics = analytics.get_session_metrics(session.id)
    assert metrics["total_trades"] == 1
    assert metrics["wins"] == 1
    assert metrics["losses"] == 0
    assert metrics["realized_pnl"] == 100.0
    assert metrics["current_capital"] == 100100.0
    
    strat_perf = analytics.get_strategy_performance(session.id)
    assert len(strat_perf) == 1
    assert strat_perf[0]["strategy"] == "momentum_v1 (v1.0)"
    assert strat_perf[0]["pnl"] == 100.0
    
    regime_perf = analytics.get_regime_performance(session.id)
    assert len(regime_perf) == 1
    assert regime_perf[0]["regime"] == "Bullish"
    assert regime_perf[0]["pnl"] == 100.0
    
    funnel = analytics.get_signal_funnel(session.id)
    assert funnel["generated"] == 2
    assert funnel["risk_approved"] == 1
    
    rejections = analytics.get_rejection_analytics(session.id)
    assert len(rejections) == 1
    assert "INSUFFICIENT_CAPITAL" in rejections[0]["reason"]
    
    ai_perf = analytics.get_ai_effectiveness(session.id)
    assert ai_perf["total_evaluated"] == 1
    assert ai_perf["accuracy"] == 1.0 # 80 score & won
