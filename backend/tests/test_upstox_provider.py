import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.data.providers.upstox_provider import UpstoxMarketDataProvider
from app.core.config import settings
import requests

@pytest.fixture
def mock_upstox_settings():
    original_token = settings.UPSTOX_ANALYTICS_TOKEN
    settings.UPSTOX_ANALYTICS_TOKEN = "mock_token"
    yield
    settings.UPSTOX_ANALYTICS_TOKEN = original_token

def test_upstox_missing_credentials():
    original_token = settings.UPSTOX_ANALYTICS_TOKEN
    settings.UPSTOX_ANALYTICS_TOKEN = None
    
    provider = UpstoxMarketDataProvider()
    with pytest.raises(ValueError, match="Upstox credentials"):
        provider._get_headers()
        
    settings.UPSTOX_ANALYTICS_TOKEN = original_token

def test_upstox_symbol_mapping():
    provider = UpstoxMarketDataProvider()
    mapping = provider._map_symbol_to_upstox("RELIANCE.NS")
    assert mapping == "NSE_EQ|INE002A01018"
    
    mapping_fallback = provider._map_symbol_to_upstox("TCS.NS")
    assert mapping_fallback == "TCS.NS"

def test_upstox_timeframe_mapping():
    provider = UpstoxMarketDataProvider()
    assert provider._map_timeframe_to_upstox_v3("1m") == ("minutes", "1")
    assert provider._map_timeframe_to_upstox_v3("1d") == ("days", "1")
    with pytest.raises(ValueError):
        provider._map_timeframe_to_upstox_v3("invalid")

@patch('app.data.providers.upstox_provider.requests.get')
def test_upstox_get_historical_success(mock_get, mock_upstox_settings):
    provider = UpstoxMarketDataProvider()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {
            "candles": [
                ["2024-03-01T00:00:00+05:30", 100.0, 110.0, 90.0, 105.0, 1000, 0],
                ["2024-03-02T00:00:00+05:30", 105.0, 115.0, 95.0, 110.0, 2000, 0]
            ]
        }
    }
    mock_get.return_value = mock_response
    
    df = provider.get_historical_ohlcv(
        "RELIANCE.NS", "1d", datetime(2024, 3, 1, tzinfo=timezone.utc), datetime(2024, 3, 2, tzinfo=timezone.utc)
    )
    
    assert not df.empty
    assert len(df) == 2
    assert "timestamp" in df.columns
    assert "close" in df.columns
    assert df.iloc[0]["close"] == 105.0
    # Chronological sort means oldest comes first
    assert df.iloc[0]["timestamp"] < df.iloc[-1]["timestamp"]

@patch('app.data.providers.upstox_provider.requests.get')
def test_upstox_get_historical_rate_limit(mock_get, mock_upstox_settings):
    provider = UpstoxMarketDataProvider()
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response
    
    with pytest.raises(RuntimeError, match="HTTP 429: Rate limited by Upstox"):
        provider.get_historical_ohlcv(
            "RELIANCE.NS", "1d", datetime(2024, 3, 1, tzinfo=timezone.utc), datetime(2024, 3, 2, tzinfo=timezone.utc)
        )
        
@patch('app.data.providers.upstox_provider.requests.get')
def test_upstox_get_historical_empty_response(mock_get, mock_upstox_settings):
    provider = UpstoxMarketDataProvider()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {
            "candles": []
        }
    }
    mock_get.return_value = mock_response
    
    df = provider.get_historical_ohlcv(
        "RELIANCE.NS", "1d", datetime(2024, 3, 1, tzinfo=timezone.utc), datetime(2024, 3, 2, tzinfo=timezone.utc)
    )
    
    assert df.empty

@patch('app.data.providers.upstox_provider.requests.get')
def test_upstox_get_historical_timeout(mock_get, mock_upstox_settings):
    provider = UpstoxMarketDataProvider()
    
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
    
    with pytest.raises(requests.exceptions.Timeout):
        provider.get_historical_ohlcv(
            "RELIANCE.NS", "1d", datetime(2024, 3, 1, tzinfo=timezone.utc), datetime(2024, 3, 2, tzinfo=timezone.utc)
        )
