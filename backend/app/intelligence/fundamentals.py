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

class YFinanceFundamentalProvider(BaseFundamentalProvider):
    """
    yfinance based Fundamental Provider.
    Note: This is an MVP / DEVELOPMENT / VALIDATION provider only.
    """
    def fetch_fundamentals(self, symbol: str, as_of: datetime) -> List[FundamentalData]:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            results = []
            
            # Mapping expected fields from yfinance
            field_map = {
                "trailingPE": "P/E",
                "forwardPE": "Forward P/E",
                "trailingEps": "EPS",
                "priceToBook": "P/B",
                "returnOnEquity": "ROE",
                "totalRevenue": "Revenue",
                "totalDebt": "Debt",
                "revenueGrowth": "Revenue Growth"
            }
            
            for yf_key, internal_metric in field_map.items():
                val = info.get(yf_key)
                if val is not None:
                    results.append(
                        FundamentalData(
                            symbol=symbol,
                            timestamp=as_of,
                            metric=internal_metric,
                            value=float(val),
                            provider_id="yfinance"
                        )
                    )
            
            return results
        except Exception as e:
            print(f"YFinance Fundamentals error for {symbol}: {e}")
            return []
