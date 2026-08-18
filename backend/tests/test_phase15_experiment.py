import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import json

from app.main import app
from app.data.database.session import SessionLocal, engine, Base
from app.data.database.models import PaperExperimentDB

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(PaperExperimentDB).delete()
    db.commit()
    yield db
    db.close()

def test_create_experiment_api(db):
    payload = {
        "name": "Test Experiment",
        "starting_capital": 50000.0,
        "execution_mode": "PAPER",
        "data_provider": "upstox",
        "timeframe": "5m",
        "watchlist": ["RELIANCE.NS"],
        "strategies": [{"name": "MomentumStrategy", "version": "1.0", "params": {}}],
        "decision_modes": ["HYBRID"],
        "risk_configuration": {"max_position_size": 10000.0},
        "ai_provider": "mock"
    }
    
    response = client.post("/api/v1/experiments/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Experiment"
    assert data["status"] == "PLANNED"
    
    # Verify DB
    exp = db.query(PaperExperimentDB).filter_by(experiment_id=data["experiment_id"]).first()
    assert exp is not None
    assert exp.execution_mode == "PAPER"
    
def test_create_experiment_rejects_live(db):
    payload = {
        "name": "Test Experiment",
        "starting_capital": 50000.0,
        "execution_mode": "LIVE", # Should be rejected
        "data_provider": "upstox",
        "timeframe": "5m",
        "watchlist": ["RELIANCE.NS"],
        "strategies": [],
        "decision_modes": ["HYBRID"],
        "risk_configuration": {}
    }
    
    response = client.post("/api/v1/experiments/", json=payload)
    assert response.status_code == 400
    assert "PAPER" in response.json()["detail"]

def test_update_experiment_status(db):
    payload = {
        "name": "Test Experiment",
        "starting_capital": 50000.0,
        "execution_mode": "PAPER",
        "data_provider": "upstox",
        "timeframe": "5m",
        "watchlist": ["RELIANCE.NS"],
        "strategies": [],
        "decision_modes": ["HYBRID"],
        "risk_configuration": {}
    }
    
    response = client.post("/api/v1/experiments/", json=payload)
    exp_id = response.json()["experiment_id"]
    
    res = client.put(f"/api/v1/experiments/{exp_id}/status?status=ACTIVE")
    assert res.status_code == 200
    
    exp = db.query(PaperExperimentDB).filter_by(experiment_id=exp_id).first()
    assert exp.status == "ACTIVE"
    assert exp.end_time is None
    
    res = client.put(f"/api/v1/experiments/{exp_id}/status?status=COMPLETED")
    assert res.status_code == 200
    
    db.refresh(exp)
    assert exp.status == "COMPLETED"
    assert exp.end_time is not None
