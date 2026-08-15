import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import List

from app.data.providers.base import MarketDataProvider

class YFinanceMarketDataProvider(MarketDataProvider):
    """
    Market Data Provider using yfinance.
    Note: This is an MVP / DEVELOPMENT / VALIDATION provider only.
    It is not guaranteed for production-grade low-latency use.
    """
    
    @property
    def provider_id(self) -> str:
        return "yfinance"
        
    def get_historical_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data using yfinance.
        """
        try:
            # Map common timeframes to yfinance intervals
            interval_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "60m", "1d": "1d", "1wk": "1wk", "1mo": "1mo"
            }
            interval = interval_map.get(timeframe.lower(), "1d")
            
            ticker = yf.Ticker(symbol)
            # yfinance returns pandas DataFrame
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
                
            # yfinance returns tz-aware index sometimes, sometimes naive. Ensure UTC.
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC')
            else:
                df.index = df.index.tz_convert('UTC')
                
            df.reset_index(inplace=True)
            
            # Map columns
            # yfinance columns are ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            # or 'Datetime' for intraday
            time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
            
            df = df.rename(columns={
                time_col: 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
            
            # Drop any duplicates
            df.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
            df.sort_values('timestamp', inplace=True)
            df.reset_index(drop=True, inplace=True)
            
            return df
            
        except Exception as e:
            # Wrap provider specific errors
            print(f"YFinance provider error fetching {symbol}: {e}")
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
            
    def get_supported_instruments(self) -> List[str]:
        # YFinance supports an enormous list, we just return a few Indian examples for MVP validation
        return ["RELIANCE.NS", "TCS.NS", "INFY.NS", "^NSEI", "^BSESN"]
