from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.data.database.session import get_db
from app.analytics.service import AnalyticsService
from pydantic import BaseModel

router = APIRouter()

class SessionStartRequest(BaseModel):
    name: str = None

class SessionResponse(BaseModel):
    id: str
    name: str
    starting_capital: float
    current_capital: float
    status: str
    execution_mode: str

@router.post("/start", response_model=SessionResponse)
def start_session(req: SessionStartRequest, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.start_session(req.name)
    return {
        "id": session.id,
        "name": session.name,
        "starting_capital": session.starting_capital,
        "current_capital": session.current_capital,
        "status": session.status,
        "execution_mode": session.execution_mode
    }

@router.post("/{session_id}/pause", response_model=SessionResponse)
def pause_session(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.pause_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "name": session.name,
        "starting_capital": session.starting_capital,
        "current_capital": session.current_capital,
        "status": session.status,
        "execution_mode": session.execution_mode
    }

@router.post("/{session_id}/resume", response_model=SessionResponse)
def resume_session(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.resume_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "name": session.name,
        "starting_capital": session.starting_capital,
        "current_capital": session.current_capital,
        "status": session.status,
        "execution_mode": session.execution_mode
    }

@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(session_id: str, db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.end_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "name": session.name,
        "starting_capital": session.starting_capital,
        "current_capital": session.current_capital,
        "status": session.status,
        "execution_mode": session.execution_mode
    }

@router.get("/current", response_model=SessionResponse)
def get_current_session(db: Session = Depends(get_db)):
    analytics = AnalyticsService(db)
    session = analytics.get_current_session()
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    return {
        "id": session.id,
        "name": session.name,
        "starting_capital": session.starting_capital,
        "current_capital": session.current_capital,
        "status": session.status,
        "execution_mode": session.execution_mode
    }
