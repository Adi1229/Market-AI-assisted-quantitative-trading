from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "project": "Market 2.0 MVP"}

def test_get_instruments():
    response = client.get("/api/v1/instruments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "symbol" in response.json()[0]

def test_get_strategies():
    response = client.get("/api/v1/strategies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # We registered multiple default strategies in dependencies.py
    assert len(response.json()) >= 2

def test_portfolio_summary():
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_value" in data
    assert data["cash"] > 0

def test_generate_mock_opportunity_and_approve():
    # 1. Generate Mock Opp
    gen_res = client.post("/api/v1/test/generate_mock_opportunity")
    assert gen_res.status_code == 200
    opp_id = gen_res.json()["opportunity_id"]
    
    # 2. Get Opp list
    list_res = client.get("/api/v1/opportunities")
    assert list_res.status_code == 200
    assert any(o["opportunity_id"] == opp_id for o in list_res.json())
    
    # 3. Approve it
    approve_res = client.post(f"/api/v1/opportunities/{opp_id}/approve", json={"current_price": 2450.0})
    if approve_res.status_code != 200:
        print(f"Failed to approve: {approve_res.json()}")
    assert approve_res.status_code == 200
    assert "executed" in approve_res.json()["message"]
    
    # 4. Check duplicate block (Idempotency)
    approve_res_2 = client.post(f"/api/v1/opportunities/{opp_id}/approve", json={"current_price": 2450.0})
    assert approve_res_2.status_code == 400
