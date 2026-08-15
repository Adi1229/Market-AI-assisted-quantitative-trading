from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

router = APIRouter()

# MVP mock list of instruments
MOCK_INSTRUMENTS = [
    {"symbol": "RELIANCE", "name": "Reliance Industries", "exchange": "NSE"},
    {"symbol": "HDFC", "name": "HDFC Bank", "exchange": "NSE"},
    {"symbol": "INFY", "name": "Infosys", "exchange": "NSE"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "exchange": "NSE"}
]

@router.get("/instruments")
def get_instruments() -> List[Dict[str, str]]:
    """Get all available registered instruments."""
    return MOCK_INSTRUMENTS

@router.get("/data/ohlcv/{symbol}")
def get_ohlcv(symbol: str) -> Dict[str, Any]:
    """Get OHLCV time series for a symbol. Returning mock data for UI MVP."""
    return {
        "symbol": symbol,
        "data": [
            {"time": "2026-08-01", "open": 100, "high": 105, "low": 98, "close": 102},
            {"time": "2026-08-02", "open": 102, "high": 108, "low": 101, "close": 107},
            {"time": "2026-08-03", "open": 107, "high": 110, "low": 105, "close": 106},
            {"time": "2026-08-04", "open": 106, "high": 109, "low": 104, "close": 108},
            {"time": "2026-08-05", "open": 108, "high": 112, "low": 107, "close": 111},
        ]
    }

@router.get("/data/features/{symbol}")
def get_features(symbol: str) -> Dict[str, Any]:
    """Get quantitative feature time series."""
    return {
        "symbol": symbol,
        "features": {
            "momentum_14": [1.2, 1.5, 2.1, 1.8, 2.4],
            "volatility_20": [0.012, 0.015, 0.014, 0.018, 0.019],
            "dates": ["2026-08-01", "2026-08-02", "2026-08-03", "2026-08-04", "2026-08-05"]
        }
    }
