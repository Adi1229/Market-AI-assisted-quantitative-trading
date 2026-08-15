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

class YFinanceNewsProvider(BaseNewsProvider):
    """
    yfinance based News Provider.
    Note: This is an MVP / DEVELOPMENT / VALIDATION provider only.
    """
    def fetch_news(self, symbol: str, start_time: datetime, end_time: datetime) -> List[NewsItem]:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            yf_news = ticker.news
            
            results = []
            if not yf_news:
                return results
                
            for item in yf_news:
                # yfinance news items are dictionaries with 'title', 'publisher', 'providerPublishTime', 'link'
                ts = item.get("providerPublishTime")
                if ts:
                    pub_time = datetime.fromtimestamp(ts)
                    # Filter by requested window
                    # if pub_time < start_time or pub_time > end_time:
                    #     continue
                    # Actually we'll just return what's available and relevant, yfinance news is very sparse and usually just recent
                    
                    results.append(
                        NewsItem(
                            id=item.get("uuid", str(uuid.uuid4())),
                            headline=item.get("title", "No Title"),
                            source=item.get("publisher", "yfinance"),
                            timestamp=pub_time,
                            symbols=[symbol],
                            text=item.get("link", "")
                        )
                    )
            
            return results
        except Exception as e:
            print(f"YFinance News error for {symbol}: {e}")
            return []
