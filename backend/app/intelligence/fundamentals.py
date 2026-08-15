from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from app.intelligence.models import FundamentalData

class BaseFundamentalProvider(ABC):
    """Abstract interface for fetching fundamental data."""
    
    @abstractmethod
    def fetch_fundamentals(self, symbol: str, as_of: datetime) -> List[FundamentalData]:
        pass

class MockFundamentalProvider(BaseFundamentalProvider):
    """Deterministic mock provider for offline testing."""
    
    def fetch_fundamentals(self, symbol: str, as_of: datetime) -> List[FundamentalData]:
        # Return deterministic mock data
        return [
            FundamentalData(
                symbol=symbol,
                timestamp=as_of,
                metric="P/E",
                value=15.5,
                provider_id="MockFund"
            ),
            FundamentalData(
                symbol=symbol,
                timestamp=as_of,
                metric="EPS",
                value=3.2,
                provider_id="MockFund"
            )
        ]
