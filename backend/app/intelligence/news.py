from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.intelligence.models import NewsItem
import uuid

class BaseNewsProvider(ABC):
    """Abstract interface for fetching news data."""
    
    @abstractmethod
    def fetch_news(self, symbol: str, start_time: datetime, end_time: datetime) -> List[NewsItem]:
        pass

class MockNewsProvider(BaseNewsProvider):
    """Deterministic mock provider for offline testing."""
    
    def fetch_news(self, symbol: str, start_time: datetime, end_time: datetime) -> List[NewsItem]:
        # Return deterministic mock data
        return [
            NewsItem(
                id=str(uuid.uuid4()),
                headline=f"{symbol} announces record profits",
                source="MockNews",
                timestamp=start_time,
                symbols=[symbol],
                text="The company saw unprecedented growth this quarter."
            ),
            NewsItem(
                id=str(uuid.uuid4()),
                headline=f"{symbol} faces regulatory scrutiny",
                source="MockNews",
                timestamp=end_time,
                symbols=[symbol],
                text="Regulators are questioning recent acquisitions."
            )
        ]
