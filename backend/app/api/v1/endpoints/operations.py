from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.database.session import get_db
from app.data.database.models import IncidentDB, HeartbeatDB, MarketHealthDB, ProviderHealthDB
from app.operations.health import health_monitor

router = APIRouter()

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    # Return overall system status
    return {"status": "HEALTHY"}

@router.get("/market-data")
def get_market_data_health(db: Session = Depends(get_db)):
    market_health = db.query(MarketHealthDB).all()
    return market_health

@router.get("/providers")
def get_provider_health(db: Session = Depends(get_db)):
    providers = db.query(ProviderHealthDB).all()
    return providers

@router.get("/heartbeat")
def get_heartbeats(db: Session = Depends(get_db)):
    heartbeats = db.query(HeartbeatDB).all()
    return heartbeats

@router.get("/incidents")
def get_incidents(resolved: bool = False, db: Session = Depends(get_db)):
    if not resolved:
        incidents = db.query(IncidentDB).filter_by(resolved=False).order_by(IncidentDB.timestamp.desc()).all()
    else:
        incidents = db.query(IncidentDB).order_by(IncidentDB.timestamp.desc()).limit(100).all()
    return incidents

@router.get("/status")
def get_overall_status(db: Session = Depends(get_db)):
    return {
        "market_open": health_monitor.is_indian_market_open(),
        "market_status": health_monitor.get_market_status(),
        "unresolved_incidents": db.query(IncidentDB).filter_by(resolved=False).count(),
        "providers_error": db.query(ProviderHealthDB).filter_by(status="ERROR").count()
    }
