# 18 — Frontend Architecture

| Field | Value |
|---|---|
| **Document ID** | FEA-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [API Specification](./17_API_SPECIFICATION.md), [ADR-003](./32_ARCHITECTURE_DECISIONS.md), [System Design](./04_SYSTEM_DESIGN.md) |

---

## 1. Technology

| Technology | Purpose | Status |
|---|---|---|
| **Next.js** | React framework with SSR | Client preference; see [ADR-003](./32_ARCHITECTURE_DECISIONS.md) |
| **React** | UI component library | Client preference |
| **Chart library** | Financial charts (candlestick, line, etc.) | TBD (candidates: Recharts, TradingView Lightweight Charts, Plotly) |
| **CSS** | Styling | TBD (CSS Modules, Tailwind, or styled-components) |
| **HTTP client** | API communication | fetch / axios / SWR |

---

## 2. Dashboard Pages

### 2.1 Page Structure

| Page | Route | Description |
|---|---|---|
| **Dashboard** | `/` | Overview: market summary, recent backtests, alerts |
| **Instruments** | `/instruments` | Browse and search instruments |
| **Instrument Detail** | `/instruments/[id]` | OHLCV chart, features, fundamentals, sentiment |
| **Strategies** | `/strategies` | List strategies, parameters, performance |
| **Backtests** | `/backtests` | Manage and view backtest runs |
| **Backtest Detail** | `/backtests/[id]` | Equity curve, trades, metrics |
| **Optimization** | `/backtests/optimize` | Parameter optimization and walk-forward |
| **ML Rankings** | `/ml/rankings` | Strategy rankings and model info |
| **News & Sentiment** | `/sentiment` | News feed, sentiment charts |
| **Fundamentals** | `/fundamentals` | Fundamental data explorer |
| **Chat** | `/chat` | AI chatbot interface |
| **Settings** | `/settings` | Provider config, feature flags |

### 2.2 Core Components

| Component | Purpose |
|---|---|
| `CandlestickChart` | OHLCV candlestick visualization |
| `LineChart` | Equity curves, sentiment trends |
| `MetricsCard` | Display performance metrics |
| `TradeTable` | Tabular trade history |
| `StrategySelector` | Strategy and parameter configuration |
| `BacktestForm` | Backtest configuration form |
| `ChatInterface` | Conversational AI interface |
| `SentimentGauge` | Visual sentiment indicator |
| `FundamentalsTable` | Fundamental metrics display |
| `InstrumentSearch` | Instrument search/autocomplete |
| `DateRangePicker` | Date range selection for data queries |
| `DataTable` | Reusable sortable/filterable table |

---

## 3. State Management

| Approach | Description |
|---|---|
| **Server state** | SWR or React Query for API data fetching and caching |
| **Local state** | React useState/useReducer for UI state |
| **URL state** | Query parameters for shareable views (date range, instrument, etc.) |

---

## 4. API Integration

```
Frontend (Next.js)  →  FastAPI Backend (/api/v1/...)
```

| Aspect | Approach |
|---|---|
| Data fetching | SWR hooks wrapping API calls |
| Loading states | Skeleton components during data load |
| Error handling | Error boundary components; toast notifications |
| Real-time updates | Polling for MVP (WebSocket for Phase 2) |

---

## 5. Responsive Design

| Breakpoint | Target |
|---|---|
| Desktop | Primary target (1280px+) |
| Tablet | Functional (768px-1279px) |
| Mobile | Basic readability (< 768px) |

Dashboard is designed primarily for desktop use (data-heavy research tool).

---

## 6. Cross-References

| Document | Relevance |
|---|---|
| [API Specification](./17_API_SPECIFICATION.md) | Backend API consumed by frontend |
| [ADR-003](./32_ARCHITECTURE_DECISIONS.md) | Frontend framework decision |
| [Security Design](./19_SECURITY_DESIGN.md) | Frontend authentication |
| [Deployment Architecture](./22_DEPLOYMENT_ARCHITECTURE.md) | Frontend deployment |
