from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from app.data.database.session import get_db
from app.analytics.service import AnalyticsService
from app.analytics.daily_report import DailyReportService
from app.data.database.models import PaperTradingSessionDB

router = APIRouter()

class SessionActionRequest(BaseModel):
    action: str # "start", "pause", "resume", "end"
    name: str = None

@router.post("/sessions")
def manage_session(req: SessionActionRequest, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    
    if req.action == "start":
        session = analytics.start_session(name=req.name)
        return {"message": "Session started", "session_id": session.id}
        
    elif req.action == "end":
        current = analytics.get_current_session()
        if not current:
            raise HTTPException(status_code=404, detail="No active session to end")
        analytics.end_session(current.id)
        return {"message": "Session ended"}
        
    elif req.action in ["pause", "resume"]:
        current = analytics.get_current_session()
        if not current and req.action == "pause":
            raise HTTPException(status_code=404, detail="No active session to pause")
            
        if req.action == "pause":
            current.status = "PAUSED"
        else:
            # resume
            paused = db.query(PaperTradingSessionDB).filter_by(status="PAUSED").order_by(PaperTradingSessionDB.updated_at.desc()).first()
            if not paused:
                raise HTTPException(status_code=404, detail="No paused session to resume")
            paused.status = "ACTIVE"
            
        db.commit()
        return {"message": f"Session {req.action}d"}
        
    raise HTTPException(status_code=400, detail="Invalid action")

@router.get("/sessions/current")
def get_current_session(db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.get_current_session()
    if session:
        return {
            "id": session.id,
            "name": session.name,
            "status": session.status,
            "starting_capital": session.starting_capital,
            "current_capital": session.current_capital,
            "start_time": session.start_time,
            "execution_mode": session.execution_mode
        }
    return {"status": "NO_SESSION"}

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.get_current_session()
    
    if not session:
        # If no active session, fetch the last completed session for display
        session = db.query(PaperTradingSessionDB).order_by(PaperTradingSessionDB.updated_at.desc()).first()
        
    if not session:
        return {"message": "No sessions found"}
        
    s_id = session.id
    
    return {
        "session": {
            "id": s_id,
            "name": session.name,
            "metrics": analytics.get_session_metrics(s_id)
        },
        "strategy_performance": analytics.get_strategy_performance(s_id),
        "regime_performance": analytics.get_regime_performance(s_id),
        "decision_mode_performance": analytics.get_decision_mode_performance(s_id),
        "signal_funnel": analytics.get_signal_funnel(s_id),
        "rejections": analytics.get_rejection_analytics(s_id),
        "ai_analysis": analytics.get_ai_effectiveness(s_id)
    }

@router.get("/daily-report")
def get_daily_report(db: Session = Depends(get_db)):
    session = db.query(PaperTradingSessionDB).filter_by(status="ACTIVE").first()
    if not session:
        session = db.query(PaperTradingSessionDB).order_by(PaperTradingSessionDB.updated_at.desc()).first()
        
    if not session:
        return {"message": "NO TRADES TODAY"}
        
    report_service = DailyReportService(db)
    return report_service.generate_daily_report(session.id)
