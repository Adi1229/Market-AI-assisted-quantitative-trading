from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.data.database.session import get_db
from app.data.database.models import PaperExperimentDB

router = APIRouter()

class ExperimentCreateRequest(BaseModel):
    name: str
    starting_capital: float
    execution_mode: str = "PAPER"
    data_provider: str
    timeframe: str
    watchlist: List[str]
    strategies: List[Dict[str, Any]]
    decision_modes: List[str]
    risk_configuration: Dict[str, Any]
    ai_provider: Optional[str] = None

class ExperimentResponse(BaseModel):
    experiment_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    starting_capital: float
    execution_mode: str
    data_provider: str
    timeframe: str
    watchlist: List[str]
    strategies: List[Dict[str, Any]]
    decision_modes: List[str]
    risk_configuration: Dict[str, Any]
    ai_provider: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ExperimentResponse)
def create_experiment(req: ExperimentCreateRequest, db: Session = Depends(get_db)):
    if req.execution_mode != "PAPER":
        raise HTTPException(status_code=400, detail="Only PAPER execution mode is allowed.")
        
    exp_id = str(uuid.uuid4())
    
    exp_db = PaperExperimentDB(
        experiment_id=exp_id,
        name=req.name,
        start_time=datetime.now(timezone.utc),
        starting_capital=req.starting_capital,
        execution_mode=req.execution_mode,
        data_provider=req.data_provider,
        timeframe=req.timeframe,
        watchlist=req.watchlist,
        strategies=req.strategies,
        decision_modes=req.decision_modes,
        risk_configuration=req.risk_configuration,
        ai_provider=req.ai_provider,
        status="PLANNED"
    )
    db.add(exp_db)
    db.commit()
    db.refresh(exp_db)
    
    return exp_db

@router.get("/", response_model=List[ExperimentResponse])
def get_experiments(db: Session = Depends(get_db)):
    return db.query(PaperExperimentDB).order_by(PaperExperimentDB.created_at.desc()).all()

@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    exp_db = db.query(PaperExperimentDB).filter_by(experiment_id=experiment_id).first()
    if not exp_db:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return exp_db

@router.put("/{experiment_id}/status")
def update_experiment_status(experiment_id: str, status: str, db: Session = Depends(get_db)):
    valid_statuses = ["PLANNED", "ACTIVE", "PAUSED", "COMPLETED", "CANCELLED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
        
    exp_db = db.query(PaperExperimentDB).filter_by(experiment_id=experiment_id).first()
    if not exp_db:
        raise HTTPException(status_code=404, detail="Experiment not found.")
        
    exp_db.status = status
    if status in ["COMPLETED", "CANCELLED"]:
        exp_db.end_time = datetime.now(timezone.utc)
        
    db.commit()
    db.refresh(exp_db)
    return {"status": exp_db.status}
