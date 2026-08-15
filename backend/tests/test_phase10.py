import pytest
import pandas as pd
from datetime import datetime, timezone
from app.data.ingestion import DataIngestionService
from app.data.providers.mock import MockMarketDataProvider
from app.engine.models import TradeOpportunity, DecisionMode, Direction, AIEvidence
from app.data.database.session import SessionLocal
    
def test_data_quality_rejection():
    # Test that invalid candles are dropped
    provider = MockMarketDataProvider()
    db = SessionLocal()
    ingestion = DataIngestionService(provider, db)
    
    # Create invalid data manually
    invalid_data = pd.DataFrame([
        {"timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc), "open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000},
        {"timestamp": datetime(2026, 1, 2, tzinfo=timezone.utc), "open": -10, "high": 110, "low": 90, "close": 105, "volume": 1000}, # invalid open
        {"timestamp": datetime(2026, 1, 3, tzinfo=timezone.utc), "open": 100, "high": 90, "low": 110, "close": 105, "volume": 1000} # high < low
    ])
    
    # Mock the provider's get_historical_ohlcv
    provider.get_historical_ohlcv = lambda *args, **kwargs: invalid_data
    
    inserted = ingestion.ingest_historical_data("TEST.NS", "1d", datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 3, tzinfo=timezone.utc))
    
    # Only 1 valid row should be inserted
    assert inserted == 1
    db.close()

def test_ai_grounding_no_fabrication():
    # Verify AI evidence schema works with empty fundamentals
    evidence = AIEvidence(
        ai_model_id="MockAI",
        ai_model_version="1.0",
        direction="BUY",
        ai_score=80.0,
        reasoning=["Missing fundamental evidence handled."],
        retrieved_facts=[], # no facts fabricated
        computed_values={},
        model_inference="Positive despite lack of fundamentals",
        uncertainty="High",
        evidence_sources=[]
    )
    assert len(evidence.retrieved_facts) == 0
    assert evidence.ai_model_id == "MockAI"
