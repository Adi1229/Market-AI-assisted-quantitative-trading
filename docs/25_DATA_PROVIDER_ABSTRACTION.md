# 25 — Data Provider Abstraction

| Field | Value |
|---|---|
| **Document ID** | DPA-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Architecture](./05_ARCHITECTURE.md), [Market Data Design](./07_MARKET_DATA_DESIGN.md), [Open Questions](./33_OPEN_QUESTIONS.md) |

---

## 1. Design Principle

> [!IMPORTANT]
> **CLIENT-CONFIRMED:** External providers must never be deeply coupled to business logic. Provider-specific assumptions must not exist in core services.

All external data sources are abstracted behind provider interfaces. This allows:

- Replacing providers without modifying business logic
- Testing with mock providers
- Supporting multiple providers simultaneously
- Migrating between providers with minimal code changes

---

## 2. Provider Interfaces

### 2.1 Market Data Provider

```python
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

class Timeframe(Enum):
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1M"

@dataclass
class OHLCVRecord:
    instrument_id: str
    timeframe: Timeframe
    timestamp: datetime        # UTC
    open: float
    high: float
    low: float
    close: float
    volume: float
    provider_id: str

@dataclass
class Instrument:
    symbol: str
    name: str
    exchange: str
    instrument_type: str       # "equity", "index"
    isin: Optional[str]
    provider_instrument_id: str
    is_active: bool

@dataclass
class CorporateAction:
    instrument_id: str
    action_type: str           # "split", "dividend", "bonus", "rights"
    ex_date: date
    record_date: Optional[date]
    details: dict              # action-specific details (ratio, amount, etc.)

class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    @abstractmethod
    async def get_instruments(
        self, exchange: Optional[str] = None,
        instrument_type: Optional[str] = None
    ) -> List[Instrument]:
        """Fetch available instruments."""
        ...

    @abstractmethod
    async def get_historical_ohlcv(
        self, instrument_id: str, timeframe: Timeframe,
        start_date: date, end_date: date
    ) -> List[OHLCVRecord]:
        """Fetch historical OHLCV data."""
        ...

    @abstractmethod
    async def get_corporate_actions(
        self, instrument_id: str,
        start_date: date, end_date: date
    ) -> List[CorporateAction]:
        """Fetch corporate actions for an instrument."""
        ...

    @abstractmethod
    async def get_supported_timeframes(self) -> List[Timeframe]:
        """Return timeframes supported by this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider availability."""
        ...
```

### 2.2 News Provider

```python
@dataclass
class NewsArticle:
    article_id: str
    title: str
    content: str
    source: str
    url: Optional[str]
    publication_time: datetime   # When article was published (UTC)
    retrieval_time: datetime     # When we retrieved it (UTC)
    provider_id: str
    raw_metadata: dict

class NewsProvider(ABC):
    """Abstract interface for news data providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @abstractmethod
    async def get_news(
        self, query: Optional[str] = None,
        instruments: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_results: int = 100
    ) -> List[NewsArticle]:
        """Fetch news articles."""
        ...

    @abstractmethod
    async def get_latest_news(
        self, instruments: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[NewsArticle]:
        """Fetch most recent news."""
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

### 2.3 Fundamental Data Provider

```python
@dataclass
class FundamentalRecord:
    instrument_id: str
    metric_name: str           # "revenue", "eps", "pe_ratio", etc.
    metric_value: float
    reporting_period: str       # "Q1-2025", "FY-2025", etc.
    reporting_date: date        # End of reporting period
    availability_date: Optional[date]  # When data became publicly available
    currency: str
    provider_id: str

class FundamentalDataProvider(ABC):
    """Abstract interface for fundamental data providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @abstractmethod
    async def get_fundamentals(
        self, instrument_id: str,
        metrics: Optional[List[str]] = None,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None
    ) -> List[FundamentalRecord]:
        """Fetch fundamental data for an instrument."""
        ...

    @abstractmethod
    async def get_available_metrics(self) -> List[str]:
        """Return metrics available from this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

### 2.4 LLM Provider

```python
@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict                 # token counts
    finish_reason: str

@dataclass
class EmbeddingResponse:
    embeddings: List[List[float]]
    model: str
    usage: dict

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @abstractmethod
    async def generate(
        self, messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """Generate a completion."""
        ...

    @abstractmethod
    async def embed(
        self, texts: List[str],
        model: Optional[str] = None
    ) -> EmbeddingResponse:
        """Generate embeddings for texts."""
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

### 2.5 Broker Provider (Phase 2+)

> [!NOTE]
> Broker integration is not part of MVP. This interface is documented for architectural planning only.

```python
class BrokerProvider(ABC):
    """Abstract interface for broker integration (Phase 2+)."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @abstractmethod
    async def place_order(self, order: dict) -> dict: ...

    @abstractmethod
    async def get_positions(self) -> List[dict]: ...

    @abstractmethod
    async def get_order_status(self, order_id: str) -> dict: ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

---

## 3. Provider Implementation Status

| Provider Interface | Candidate Implementations | Status |
|---|---|---|
| `MarketDataProvider` | DhanHQ (mentioned by client), others TBD | TBD — to be verified |
| `NewsProvider` | TBD | TBD |
| `FundamentalDataProvider` | TBD | TBD |
| `LLMProvider` | TBD | TBD |
| `BrokerProvider` | TBD (Phase 2+) | Phase 2+ |

> [!WARNING]
> Provider capabilities, API limits, data coverage, pricing, and historical data availability have **not been verified**. These are marked as "to be verified" per project guidelines.

---

## 4. Provider Configuration

Providers are configured via environment variables and configuration files:

```yaml
# Example provider configuration (conceptual)
providers:
  market_data:
    active: "dhan"  # or other provider key
    dhan:
      api_key: "${DHAN_API_KEY}"  # from environment
      base_url: "https://api.dhan.co"  # to be verified
      rate_limit: null  # to be verified
    # Additional providers can be added here

  news:
    active: null  # TBD
    # Provider-specific config when selected

  fundamentals:
    active: null  # TBD

  llm:
    active: null  # TBD
```

---

## 5. Provider Factory

```python
class ProviderFactory:
    """Factory for creating provider instances based on configuration."""

    _market_data_providers: Dict[str, Type[MarketDataProvider]] = {}
    _news_providers: Dict[str, Type[NewsProvider]] = {}
    _fundamental_providers: Dict[str, Type[FundamentalDataProvider]] = {}
    _llm_providers: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register_market_data_provider(
        cls, key: str, provider_class: Type[MarketDataProvider]
    ):
        cls._market_data_providers[key] = provider_class

    @classmethod
    def create_market_data_provider(cls, config: dict) -> MarketDataProvider:
        key = config["active"]
        provider_class = cls._market_data_providers[key]
        return provider_class(config[key])
```

---

## 6. Mock Providers (Testing)

Every provider interface shall have a corresponding mock implementation for testing:

| Mock Provider | Purpose |
|---|---|
| `MockMarketDataProvider` | Returns configurable test data for unit/integration tests |
| `MockNewsProvider` | Returns sample news articles |
| `MockFundamentalDataProvider` | Returns sample fundamental data |
| `MockLLMProvider` | Returns configurable responses |

---

## 7. Provider Selection Guidelines

| Criterion | Consideration |
|---|---|
| Data coverage | Must cover required instruments and timeframes |
| Historical depth | Must meet backtesting requirements |
| API reliability | Uptime, rate limits, error handling |
| Data quality | Accuracy, corporate action handling, timeliness |
| Cost | API subscription pricing |
| Terms of service | Data redistribution, storage, usage restrictions |

> [!IMPORTANT]
> Do not implement provider-specific assumptions in core services. All provider-specific logic must remain within the provider implementation class.

---

## 8. Cross-References

| Document | Relevance |
|---|---|
| [Market Data Design](./07_MARKET_DATA_DESIGN.md) | Market data ingestion details |
| [News Sentiment Design](./14_NEWS_SENTIMENT_DESIGN.md) | News provider usage |
| [Fundamental Analysis](./15_FUNDAMENTAL_ANALYSIS_DESIGN.md) | Fundamental provider usage |
| [AI Chatbot Design](./16_AI_RAG_CHATBOT_DESIGN.md) | LLM provider usage |
| [Open Questions](./33_OPEN_QUESTIONS.md) | Provider selection questions |
| [Security Design](./19_SECURITY_DESIGN.md) | Provider credential management |
