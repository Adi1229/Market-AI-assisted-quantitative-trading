from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from typing import List, Optional

class MarketDataProvider(ABC):
    """Abstract base class for all market data providers."""
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Returns the unique identifier for this provider (e.g., 'dhan', 'mock')."""
        pass
        
    @abstractmethod
    def get_historical_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data.
        
        Returns a DataFrame with columns:
        ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        The timestamp must be timezone-aware (UTC).
        """
        pass
        
    @abstractmethod
    def get_supported_instruments(self) -> List[str]:
        """Returns a list of supported instrument symbols."""
        pass
