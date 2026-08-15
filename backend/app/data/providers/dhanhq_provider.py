import pandas as pd
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.config import settings
from app.data.providers.base import MarketDataProvider

logger = logging.getLogger(__name__)

class DhanMarketDataProvider(MarketDataProvider):
    """
    Market Data Provider adapter for DhanHQ.
    Uses Dhan Data APIs to fetch OHLCV data.
    """
    def __init__(self):
        self.client_id = settings.DHAN_CLIENT_ID
        self.access_token = settings.DHAN_ACCESS_TOKEN
        self.base_url = "https://api.dhan.co"
        
        # Dhan expects specific exchange segment mapping
        # 1 = NSE_EQ, 2 = NSE_FNO, etc.
        self.exchange_segment_map = {
            "NSE": "NSE_EQ",
            "BSE": "BSE_EQ"
        }
        
    @property
    def provider_id(self) -> str:
        return "dhanhq"
        
    def get_supported_instruments(self) -> list[str]:
        return ["RELIANCE.NS", "^NSEI"]
        
    def _get_headers(self) -> Dict[str, str]:
        if not self.client_id or not self.access_token:
            raise ValueError("DhanHQ credentials (DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN) are missing.")
        return {
            "client-id": self.client_id,
            "access-token": self.access_token,
            "Content-Type": "application/json"
        }
        
    def _map_symbol_to_dhan(self, symbol: str) -> Dict[str, Any]:
        """
        Maps internal symbol (e.g. RELIANCE.NS) to Dhan format.
        For MVP, we use hardcoded mapping or simple heuristics.
        """
        # MVP Mapping
        mapping = {
            "RELIANCE.NS": {"security_id": "2885", "exchange": "NSE_EQ"},
            "^NSEI": {"security_id": "13", "exchange": "IDX_I"} # Nifty 50 Index
        }
        
        if symbol in mapping:
            return mapping[symbol]
            
        # Fallback heuristic
        if symbol.endswith(".NS"):
            return {"security_id": symbol.replace(".NS", ""), "exchange": "NSE_EQ"}
        return {"security_id": symbol, "exchange": "NSE_EQ"}

    def _map_timeframe_to_dhan(self, timeframe: str) -> str:
        """
        Maps internal timeframe (e.g. '1d', '5m') to Dhan interval.
        Dhan supports: 1, 5, 15, 25, 60, D, W, M.
        """
        mapping = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60",
            "1d": "D",
            "1wk": "W",
            "1mo": "M"
        }
        if timeframe not in mapping:
            raise ValueError(f"Unsupported Dhan timeframe: {timeframe}")
        return mapping[timeframe]

    def get_historical_ohlcv(
        self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetches historical data from DhanHQ Data API.
        """
        headers = self._get_headers()
        
        dhan_sym = self._map_symbol_to_dhan(symbol)
        dhan_interval = self._map_timeframe_to_dhan(timeframe)
        
        # DhanHQ format for dates: YYYY-MM-DD
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        payload = {
            "securityId": dhan_sym["security_id"],
            "exchangeSegment": dhan_sym["exchange"],
            "instrument": "EQUITY", # Simplified for MVP
            "fromDate": from_date,
            "toDate": to_date,
            "interval": dhan_interval
        }
        
        url = f"{self.base_url}/charts/historical"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 429:
                logger.error(f"DhanHQ rate limit exceeded for {symbol}")
                raise RuntimeError(f"HTTP 429: Rate limited by DhanHQ")
                
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") != "success":
                logger.warning(f"Dhan API returned failure status: {data}")
                return pd.DataFrame()
                
            chart_data = data.get("data", {})
            if not chart_data:
                return pd.DataFrame()
                
            # Parse Dhan Response
            # typically: 'start_Time': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(chart_data.get("start_Time", []), unit='s', utc=True),
                "open": chart_data.get("open", []),
                "high": chart_data.get("high", []),
                "low": chart_data.get("low", []),
                "close": chart_data.get("close", []),
                "volume": chart_data.get("volume", [])
            })
            
            # Normalize column names just in case
            df["symbol"] = symbol
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from DhanHQ for {symbol}: {e}")
            raise
