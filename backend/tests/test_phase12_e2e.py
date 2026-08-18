import pytest
from datetime import datetime, timedelta, timezone
from app.data.database.session import SessionLocal
from app.engine.models import DecisionMode, Direction, TradeOpportunity, StrategyEvidence, AIEvidence
from app.engine.workflow import WorkflowOrchestrator
from app.engine.risk import RiskEngine
from app.engine.execution import PaperExecutionProvider
from app.engine.portfolio import VirtualPortfolio
from app.engine.notification import MockTelegramAdapter
from app.data.database.models import PaperTradingJournalDB

@pytest.mark.anyio
async def test_phase12_e2e_paper_trading():
    db = SessionLocal()
    
    portfolio = VirtualPortfolio(initial_capital=100000.0)
    portfolio.load_from_db(db)
    
    execution = PaperExecutionProvider(portfolio)
    risk = RiskEngine()
    notification = MockTelegramAdapter()
    
    workflow = WorkflowOrchestrator(risk, execution, notification)
    
    now = datetime.now(timezone.utc)
    
    strat_ev = StrategyEvidence(
        strategy_id="momentum", strategy_name="Momentum", strategy_version="1.0",
        parameters={}, signal_type="BUY", signal_score=85.0, features_used={}, explanation="Strong momentum"
    )
    ai_ev = AIEvidence(
        ai_model_id="MockAI", ai_model_version="1.0", direction="BUY", ai_score=90.0,
        reasoning=["Bullish trend"], retrieved_facts=[], computed_values={}, model_inference="Strong Buy",
        uncertainty="Low", evidence_sources=[]
    )
    
    import uuid
    test_symbol = f"TEST_{uuid.uuid4().hex[:6]}"
    
    opp = TradeOpportunity(
        symbol=test_symbol,
        instrument_id=test_symbol,
        timestamp=now,
        decision_mode=DecisionMode.HYBRID,
        direction=Direction.BUY,
        confidence_score=87.5,
        strategy_version="1.0",
        ai_confidence=0.9,
        hybrid_score=87.5,
        strategy_evidence=strat_ev,
        ai_evidence=ai_ev,
        market_regime="Bullish",
        reasoning=[],
        data_references=[],
        risk_level="LOW",
        suggested_position_size=10.0
    )
    
    # 1. Process New Opp
    await workflow.process_new_opportunity(opp, current_price=3500.0, db=db)
    print("RISK REASONING:", opp.reasoning)
    assert opp.status.value == "AWAITING_APPROVAL"
    
    # 2. Take Trade
    order = await workflow.process_user_action(opp, "TAKE_TRADE", current_price=3500.0, db=db)
    assert order is not None
    assert order.status == "filled"
    assert opp.status.value == "EXECUTED"
    
    # 3. Verify Position
    positions = portfolio.get_positions()
    pos = next((p for p in positions if p.instrument_id == test_symbol), None)
    assert pos is not None
    
    # 4. Verify Journal (Open)
    journals = db.query(PaperTradingJournalDB).filter_by(opportunity_id=opp.opportunity_id).all()
    assert len(journals) == 1
    assert journals[0].exit_price is None
    
    # 5. Simulate closing trade (SELL)
    sell_opp = TradeOpportunity(
        symbol=test_symbol,
        instrument_id=test_symbol,
        timestamp=now + timedelta(hours=1),
        decision_mode=DecisionMode.HYBRID,
        direction=Direction.SELL,
        confidence_score=90.0,
        market_regime="Bearish",
        reasoning=[],
        data_references=[],
        risk_level="LOW",
        suggested_position_size=10.0
    )
    
    await workflow.process_new_opportunity(sell_opp, current_price=3600.0, db=db)
    sell_order = await workflow.process_user_action(sell_opp, "TAKE_TRADE", current_price=3600.0, db=db)
    
    assert sell_order is not None
    pos_after_sell = next((p for p in portfolio.get_positions() if p.instrument_id == test_symbol), None)
    assert pos_after_sell is None # Closed
    
    # 6. Verify Journal (Closed)
    journals_closed = db.query(PaperTradingJournalDB).filter_by(opportunity_id=opp.opportunity_id).all()
    assert len(journals_closed) == 1
    assert journals_closed[0].exit_price is not None
    assert journals_closed[0].realized_pnl > 0 # (3600 - 3500) * 10 - comm/slippage
    
    db.close()
