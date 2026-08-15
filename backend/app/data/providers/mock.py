import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List
from app.data.providers.base import MarketDataProvider

class MockMarketDataProvider(MarketDataProvider):
    """Mock provider for testing without external API calls."""
    
    @property
    def provider_id(self) -> str:
        return "mock"
        
    def get_historical_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        
        # Determine frequency
        freq = 'D'
        if timeframe in ['1m', '5m', '15m', '1h']:
            freq = timeframe.replace('m', 'min').replace('h', 'h')
            
        dates = pd.date_range(start=start_date, end=end_date, freq=freq, tz='UTC')
        
        if len(dates) == 0:
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
        # Generate random walk
        np.random.seed(hash(symbol) % (2**32)) # consistent random walk per symbol
        returns = np.random.normal(0, 0.01, len(dates))
        price = 100 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': price * np.random.uniform(0.99, 1.01, len(dates)),
            'close': price,
            'high': price * np.random.uniform(1.0, 1.02, len(dates)),
            'low': price * np.random.uniform(0.98, 1.0, len(dates)),
            'volume': np.random.randint(1000, 1000000, len(dates))
        })
        
        # Ensure high is highest, low is lowest
        df['high'] = df[['open', 'close', 'high']].max(axis=1)
        df['low'] = df[['open', 'close', 'low']].min(axis=1)
        
        return df
        
    def get_supported_instruments(self) -> List[str]:
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "NIFTY50"]
