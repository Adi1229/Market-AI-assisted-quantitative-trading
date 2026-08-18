from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.data.database.session import get_db
from app.analytics.service import AnalyticsService
from app.api.schemas import PerformanceAnalyticsResponse
from app.data.database.models import PaperTradingJournalDB, TradeOpportunityDB

router = APIRouter()

@router.get("/performance", response_model=PerformanceAnalyticsResponse)
def get_performance_analytics(db: Session = Depends(get_db)):
    trades = db.query(PaperTradingJournalDB).filter(PaperTradingJournalDB.exit_price != None).all()
    
    total_trades = len(trades)
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0.0
    total_win = 0.0
    total_loss = 0.0
    
    strategy_metrics: Dict[str, Any] = {}
    
    for t in trades:
        pnl = t.realized_pnl or 0.0
        total_pnl += pnl
        
        # Strategy breakdown
        strat = t.strategy or "unknown"
        if strat not in strategy_metrics:
            strategy_metrics[strat] = {"trades": 0, "wins": 0, "pnl": 0.0}
            
        strategy_metrics[strat]["trades"] += 1
        strategy_metrics[strat]["pnl"] += pnl
        
        if pnl > 0:
            winning_trades += 1
            total_win += pnl
            strategy_metrics[strat]["wins"] += 1
        else:
            losing_trades += 1
            total_loss += abs(pnl)
            
    win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0
    avg_win = (total_win / winning_trades) if winning_trades > 0 else 0.0
    avg_loss = (total_loss / losing_trades) if losing_trades > 0 else 0.0
    profit_factor = (total_win / total_loss) if total_loss > 0 else (float('inf') if total_win > 0 else 0.0)
    
    # Calculate AI agreement rate on completed trades
    agreements = 0
    valid_ai_trades = 0
    for t in trades:
        if t.ai_score is not None and t.strategy:
            valid_ai_trades += 1
            if (t.ai_score >= 50.0 and t.direction == "BUY") or (t.ai_score < 50.0 and t.direction == "SELL"):
                agreements += 1
                
    ai_agreement_rate = (agreements / valid_ai_trades * 100.0) if valid_ai_trades > 0 else 0.0
    
    return PerformanceAnalyticsResponse(
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
        total_pnl=total_pnl,
        average_win=avg_win,
        average_loss=avg_loss,
        profit_factor=profit_factor,
        ai_agreement_rate=ai_agreement_rate,
        strategy_metrics=strategy_metrics
    )

@router.get("/strategy")
def get_strategy_performance(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_strategy_performance(session_id)

@router.get("/regime")
def get_regime_performance(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_regime_performance(session_id)

@router.get("/decision-mode")
def get_decision_mode_performance(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_decision_mode_performance(session_id)

@router.get("/funnel")
def get_signal_funnel(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_signal_funnel(session_id)

@router.get("/rejections")
def get_rejections(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_rejection_analytics(session_id)

@router.get("/ai-effectiveness")
def get_ai_effectiveness(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_ai_effectiveness(session_id)

@router.get("/daily-report")
def get_daily_report(db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    return analytics.get_daily_report()
