import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.data.providers.dhanhq_provider import DhanMarketDataProvider
from app.core.config import settings

@pytest.fixture
def mock_dhan_settings():
    original_client = settings.DHAN_CLIENT_ID
    original_token = settings.DHAN_ACCESS_TOKEN
    settings.DHAN_CLIENT_ID = "mock_client"
    settings.DHAN_ACCESS_TOKEN = "mock_token"
    yield
    settings.DHAN_CLIENT_ID = original_client
    settings.DHAN_ACCESS_TOKEN = original_token

def test_dhan_missing_credentials():
    original_client = settings.DHAN_CLIENT_ID
    settings.DHAN_CLIENT_ID = None
    
    provider = DhanMarketDataProvider()
    with pytest.raises(ValueError, match="DhanHQ credentials"):
        provider._get_headers()
        
    settings.DHAN_CLIENT_ID = original_client

def test_dhan_symbol_mapping():
    provider = DhanMarketDataProvider()
    mapping = provider._map_symbol_to_dhan("RELIANCE.NS")
    assert mapping["exchange"] == "NSE_EQ"
    assert mapping["security_id"] == "2885"
    
    mapping_fallback = provider._map_symbol_to_dhan("TCS.NS")
    assert mapping_fallback["exchange"] == "NSE_EQ"
    assert mapping_fallback["security_id"] == "TCS"

def test_dhan_timeframe_mapping():
    provider = DhanMarketDataProvider()
    assert provider._map_timeframe_to_dhan("1m") == "1"
    assert provider._map_timeframe_to_dhan("1d") == "D"
    with pytest.raises(ValueError):
        provider._map_timeframe_to_dhan("invalid")

@patch('app.data.providers.dhanhq_provider.requests.post')
def test_dhan_get_historical_success(mock_post, mock_dhan_settings):
    provider = DhanMarketDataProvider()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {
            "start_Time": [1700000000, 1700086400],
            "open": [100.0, 105.0],
            "high": [110.0, 115.0],
            "low": [90.0, 95.0],
            "close": [105.0, 110.0],
            "volume": [1000, 2000]
        }
    }
    mock_post.return_value = mock_response
    
    df = provider.get_historical_ohlcv(
        "RELIANCE.NS", "1d", datetime(2023, 1, 1, tzinfo=timezone.utc), datetime(2023, 1, 31, tzinfo=timezone.utc)
    )
    
    assert not df.empty
    assert len(df) == 2
    assert "timestamp" in df.columns
    assert "close" in df.columns
    assert df.iloc[0]["close"] == 105.0

@patch('app.data.providers.dhanhq_provider.requests.post')
def test_dhan_get_historical_rate_limit(mock_post, mock_dhan_settings):
    provider = DhanMarketDataProvider()
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_post.return_value = mock_response
    
    with pytest.raises(RuntimeError, match="HTTP 429: Rate limited by DhanHQ"):
        provider.get_historical_ohlcv(
            "RELIANCE.NS", "1d", datetime(2023, 1, 1, tzinfo=timezone.utc), datetime(2023, 1, 31, tzinfo=timezone.utc)
        )
