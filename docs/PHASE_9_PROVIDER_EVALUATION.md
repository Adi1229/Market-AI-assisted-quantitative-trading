# Phase 9 — Production Provider Evaluation

| Field | Value |
|---|---|
| **Document ID** | EVAL-001 |
| **Version** | 1.0.0 |
| **Status** | Final |
| **Last Updated** | 2026-08-15 |

---

## 1. Objective

Phase 8 testing revealed that the current MVP market data provider (`yfinance`) is subject to aggressive server-side rate limiting (HTTP 429 Too Many Requests) by Yahoo Finance when used for programmatic trading systems. While it served its purpose for initial offline development and structural validation, it is **unsuitable for production or reliable paper-trading automation**, particularly for the Indian equity market where timezone and exchange conventions are often mishandled by international fallback APIs.

This evaluation reviews Indian-market-focused data providers to replace `yfinance` for production deployment.

---

## 2. Evaluation Criteria

Providers are evaluated based on:
- **Market Coverage**: Support for NSE/BSE equities, indices, and derivatives.
- **Historical Data**: Availability of daily and intraday (minute-level) OHLCV data.
- **API Reliability & Rate Limits**: Suitability for programmatic execution.
- **Authentication**: Token lifecycle and automated login capabilities.
- **Cost**: Startup/MVP friendly vs. enterprise pricing.
- **Documentation**: Quality of API references and SDKs.

---

## 3. Provider Candidates

### 3.1 DhanHQ (RECOMMENDED)

DhanHQ has emerged as a developer-friendly broker API in the Indian market.

**Pros:**
- **Trading APIs:** Free of charge (order execution, portfolio management).
- **Data APIs:** ₹499/month for comprehensive historical and live data (very cost-effective for MVP).
- **Historical Depth:** Deep intraday (1m, 5m) and daily historical OHLCV data across NSE/BSE/MCX.
- **Authentication:** JWT-based access tokens with 30-day validity, significantly reducing daily automated login friction compared to competitors.
- **WebSockets:** Real-time market data streaming available.

**Cons:**
- Data API is not entirely free (requires ₹499/mo subscription), but this is standard/cheap for reliable Indian market data.

**Verdict: RECOMMENDED**
DhanHQ offers the best balance of cost, developer experience, and data reliability for transitioning this MVP to a production-ready paper/live trading system.

### 3.2 Zerodha Kite Connect (ALTERNATIVE)

The industry standard and most mature API in the Indian retail broking space.

**Pros:**
- Highly reliable, excellent documentation, massive community.
- Deep historical data via their historical API.

**Cons:**
- Expensive for early stage (₹2000/mo for trading + ₹2000/mo for historical data = ₹4000/month).
- Strict daily authentication requirements (requires manual login flow every morning), making fully headless autonomous trading complex to orchestrate without workarounds.

**Verdict: ALTERNATIVE**
Best for well-capitalized or later-stage production, but too expensive and restrictive on authentication for the current MVP phase.

### 3.3 Angel One SmartAPI (ALTERNATIVE)

**Pros:**
- Free API access for trading and historical data.
- Good coverage of Indian markets.

**Cons:**
- Historically reported API stability issues and rate limit inconsistencies compared to Zerodha.
- Documentation can be fragmented.

**Verdict: ALTERNATIVE**
A viable free alternative to DhanHQ, but developer experience is often cited as inferior.

### 3.4 Upstox Developer API (ALTERNATIVE)

**Pros:**
- Free API access (recently updated pricing).
- Historical data available.

**Cons:**
- Evolving API surface, slightly less community tooling than Zerodha.

**Verdict: ALTERNATIVE**
Another viable free option, similar to Angel One.

### 3.5 Yahoo Finance / `yfinance` (CURRENT MVP - DEFERRED)

**Pros:**
- Completely free, no API keys, no account needed.

**Cons:**
- **Strictly Rate Limited (HTTP 429)**: Proved unreliable in Phase 8 tests.
- **Data Quality**: Frequent issues with Indian stock splits, dividends, and timezone alignments.
- **Intraday Limits**: Very limited history for 1m/5m data.

**Verdict: DEFERRED (Retain as Mock/Fallback only)**
Must not be used for production execution. Kept in the codebase solely for `DATA_PROVIDER=mock` offline testing and structural validation.

---

## 4. Implementation Strategy

1. **Retain Provider Factory**: The `DATA_PROVIDER` environment variable will continue to dictate the active provider.
2. **Current Default**: `DATA_PROVIDER=mock` remains the default to ensure tests run offline.
3. **Future Action**: The user must select a production provider (e.g., DhanHQ), obtain API keys, and implement the `MarketDataProvider` abstract interface inside `app/data/providers/`.
4. **No Core Changes**: The Signal Engine, Risk Engine, and Execution Engine require zero code changes when the provider is swapped, as validated in Phase 8.
