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
        self.base_url = "https://api.upstox.com/v3"
        
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

    def _map_timeframe_to_upstox_v3(self, timeframe: str) -> tuple[str, str]:
        """
        Maps internal timeframe (e.g. '1d', '1m') to Upstox V3 unit and interval.
        Returns: (unit, interval)
        """
        mapping = {
            "1m": ("minutes", "1"),
            "5m": ("minutes", "5"),
            "15m": ("minutes", "15"),
            "30m": ("minutes", "30"),
            "1h": ("hours", "1"),
            "1d": ("days", "1"),
            "1wk": ("weeks", "1"),
            "1mo": ("months", "1")
        }
        if timeframe not in mapping:
            raise ValueError(f"Unsupported Upstox timeframe: {timeframe}")
        return mapping[timeframe]

    def get_historical_ohlcv(
        self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetches historical data from Upstox Historical Candle API V3.
        URL format: /historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
        Dates should be in yyyy-mm-dd format.
        """
        headers = self._get_headers()
        
        instrument_key = self._map_symbol_to_upstox(symbol)
        unit, interval = self._map_timeframe_to_upstox_v3(timeframe)
        
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = end_date.strftime("%Y-%m-%d")
        
        # Determine endpoints
        historical_url = f"{self.base_url}/historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}"
        intraday_url = None
        
        # If intraday timeframe and end_date includes today, fetch intraday data too
        if unit in ["minutes", "hours"] and end_date.date() >= datetime.now(timezone.utc).date():
            intraday_url = f"{self.base_url}/historical-candle/intraday/{instrument_key}/{unit}/{interval}"
            
        all_candles = []
        
        try:
            # 1. Fetch historical
            hist_resp = requests.get(historical_url, headers=headers, timeout=10)
            if hist_resp.status_code == 429:
                raise RuntimeError(f"HTTP 429: Rate limited by Upstox")
            if hist_resp.status_code == 200:
                hist_data = hist_resp.json()
                if hist_data.get("status") == "success":
                    all_candles.extend(hist_data.get("data", {}).get("candles", []))
                    
            # 2. Fetch intraday (freshness)
            if intraday_url:
                intra_resp = requests.get(intraday_url, headers=headers, timeout=10)
                if intra_resp.status_code == 429:
                    raise RuntimeError(f"HTTP 429: Rate limited by Upstox")
                if intra_resp.status_code == 200:
                    intra_data = intra_resp.json()
                    if intra_data.get("status") == "success":
                        all_candles.extend(intra_data.get("data", {}).get("candles", []))
            
            if not all_candles:
                return pd.DataFrame()
                
            # Upstox candle format: [timestamp, open, high, low, close, volume, oi]
            # timestamp is ISO8601 string e.g. "2024-03-01T00:00:00+05:30"
            records = []
            seen_timestamps = set()
            for candle in all_candles:
                if len(candle) >= 6:
                    ts, o, h, l, c, v = candle[:6]
                    if ts not in seen_timestamps:
                        seen_timestamps.add(ts)
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
