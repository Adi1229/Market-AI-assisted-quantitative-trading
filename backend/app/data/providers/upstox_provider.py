import pandas as pd
import requests
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.core.config import settings
from app.data.providers.base import MarketDataProvider

logger = logging.getLogger(__name__)

class UpstoxMarketDataProvider(MarketDataProvider):
    """
    Market Data Provider adapter for Upstox.
    Uses Upstox API v2 to fetch historical OHLCV data.
    """
    def __init__(self):
        self.analytics_token = settings.UPSTOX_ANALYTICS_TOKEN
        self.base_url = "https://api.upstox.com/v2"
        
    @property
    def provider_id(self) -> str:
        return "upstox"
        
    def get_supported_instruments(self) -> list[str]:
        return ["RELIANCE.NS", "^NSEI"]
        
    def _get_headers(self) -> Dict[str, str]:
        if not self.analytics_token:
            raise ValueError("Upstox credentials (UPSTOX_ANALYTICS_TOKEN) are missing.")
        return {
            "Authorization": f"Bearer {self.analytics_token}",
            "Accept": "application/json"
        }
        
    def _map_symbol_to_upstox(self, symbol: str) -> str:
        """
        Maps internal symbol (e.g. RELIANCE.NS) to Upstox instrument_key.
        """
        mapping = {
            "RELIANCE.NS": "NSE_EQ|INE002A01018",
            "^NSEI": "NSE_INDEX|Nifty 50"
        }
        return mapping.get(symbol, symbol)

    def _map_timeframe_to_upstox(self, timeframe: str) -> str:
        """
        Maps internal timeframe (e.g. '1d', '1m') to Upstox interval.
        Upstox v2 supports: 1minute, 30minute, day, etc.
        """
        mapping = {
            "1m": "1minute",
            "5m": "5minute",
            "15m": "15minute",
            "30m": "30minute",
            "1h": "60minute",
            "1d": "day",
            "1wk": "week",
            "1mo": "month"
        }
        if timeframe not in mapping:
            raise ValueError(f"Unsupported Upstox timeframe: {timeframe}")
        return mapping[timeframe]

    def get_historical_ohlcv(
        self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetches historical data from Upstox Historical Candle API.
        URL format: /historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}
        Dates should be in yyyy-mm-dd format.
        """
        headers = self._get_headers()
        
        instrument_key = self._map_symbol_to_upstox(symbol)
        interval = self._map_timeframe_to_upstox(timeframe)
        
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Upstox v2 URL structure for historical candles
        url = f"{self.base_url}/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429:
                logger.error(f"Upstox rate limit exceeded for {symbol}")
                raise RuntimeError(f"HTTP 429: Rate limited by Upstox")
                
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") != "success":
                logger.warning(f"Upstox API returned failure status: {data}")
                return pd.DataFrame()
                
            candles = data.get("data", {}).get("candles", [])
            if not candles:
                return pd.DataFrame()
                
            # Upstox candle format: [timestamp, open, high, low, close, volume, oi]
            # timestamp is ISO8601 string e.g. "2024-03-01T00:00:00+05:30"
            records = []
            for candle in candles:
                if len(candle) >= 6:
                    ts, o, h, l, c, v = candle[:6]
                    records.append({
                        "timestamp": pd.to_datetime(ts, utc=True),
                        "open": float(o),
                        "high": float(h),
                        "low": float(l),
                        "close": float(c),
                        "volume": int(v)
                    })
                    
            df = pd.DataFrame(records)
            df["symbol"] = symbol
            
            # Ensure chronological order (Upstox typically returns newest first)
            df = df.sort_values("timestamp").reset_index(drop=True)
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Upstox for {symbol}: {e}")
            raise
