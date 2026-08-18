import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# Force setting of test token before we import client routes
settings.MARKET_API_TOKEN = "test-secret-token"

client = TestClient(app)

def test_public_health_endpoint():
    response = client.get("/api/v1/health")
    # Health endpoint should be public
    assert response.status_code == 200

def test_protected_endpoint_without_token():
    # e.g., get portfolio
    response = client.get("/api/v1/portfolio/summary")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_endpoint_with_invalid_token():
    response = client.get("/api/v1/portfolio/summary", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication token"

def test_protected_endpoint_with_valid_token():
    response = client.get("/api/v1/portfolio/summary", headers={"Authorization": f"Bearer {settings.MARKET_API_TOKEN}"})
    assert response.status_code == 200

def test_approve_without_token():
    response = client.post("/api/v1/opportunities/123/approve", json={"current_price": 100.0})
    assert response.status_code == 401

def test_approve_with_invalid_token():
    response = client.post("/api/v1/opportunities/123/approve", json={"current_price": 100.0}, headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401

def test_approve_with_valid_token_executes_logic():
    # We test with valid token. Since opportunity 123 doesn't exist, it should return 404 or some business logic error, not 401
    response = client.post("/api/v1/opportunities/123/approve", json={"current_price": 100.0}, headers={"Authorization": f"Bearer {settings.MARKET_API_TOKEN}"})
    assert response.status_code != 401
    assert response.status_code in [404, 400, 200]

def test_ignore_without_token():
    response = client.post("/api/v1/opportunities/123/ignore", json={"current_price": 100.0})
    assert response.status_code == 401

def test_portfolio_without_token():
    response = client.get("/api/v1/portfolio/positions")
    assert response.status_code == 401

def test_operations_without_token():
    response = client.get("/api/v1/operations/status")
    assert response.status_code == 401
