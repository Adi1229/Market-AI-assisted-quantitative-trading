# 17 — API Specification

| Field | Value |
|---|---|
| **Document ID** | API-001 |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Frontend Architecture](./18_FRONTEND_ARCHITECTURE.md), [Execution Engine](./37_EXECUTION_ENGINE.md), [Signal Engine](./36_SIGNAL_ENGINE.md) |

---

## 1. Overview

The platform exposes a REST API built with FastAPI. It handles operations for data retrieval, strategy management, backtesting, signal monitoring, risk management, and user approval of trades.

---

## 2. Market Data Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/instruments` | GET | List all registered instruments |
| `/api/v1/data/ohlcv/{symbol}` | GET | Get OHLCV time series |
| `/api/v1/data/features/{symbol}` | GET | Get computed feature time series |
| `/api/v1/data/ingest` | POST | Trigger manual ingestion |

---

## 3. Strategy Studio Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/strategies` | GET | List all registered strategies (Strategy Studio) |
| `/api/v1/strategies/{strategy_id}` | GET | Get strategy metadata and parameters |
| `/api/v1/strategies/{strategy_id}/activate` | POST | Set strategy status to ACTIVE |
| `/api/v1/strategies/{strategy_id}/deactivate` | POST | Set strategy status to INACTIVE |

---

## 4. Backtesting Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/backtests` | POST | Run a new backtest |
| `/api/v1/backtests/{backtest_id}` | GET | Get full backtest results and metrics |
| `/api/v1/backtests/{backtest_id}/trades` | GET | Get individual trades from a backtest |

---

## 5. Signal Engine & Opportunity Endpoints (New)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/opportunities` | GET | List recent trade opportunities |
| `/api/v1/opportunities/{opp_id}` | GET | Get full evidence (Strategy, AI, Hybrid scores) |
| `/api/v1/opportunities/{opp_id}/approve` | POST | User approves trade (TAKE_TRADE) |
| `/api/v1/opportunities/{opp_id}/ignore` | POST | User rejects trade (IGNORE) |
| `/api/v1/signal-engine/mode` | PUT | Configure active decision mode (STRATEGY_ONLY, AI_ONLY, HYBRID) |

---

## 6. Execution & Portfolio Endpoints (New)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/execution/mode` | PUT | Configure execution mode (PAPER, LIVE) |
| `/api/v1/execution/status` | GET | Get execution engine health and active mode |
| `/api/v1/portfolio/summary` | GET | Get virtual/live portfolio summary and P&L |
| `/api/v1/portfolio/positions` | GET | Get open positions |
| `/api/v1/portfolio/orders` | GET | Get recent orders |

---

## 7. AI & Chatbot Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/chat` | POST | Send message to AI chatbot |
| `/api/v1/chat/history` | GET | Retrieve conversation history |
| `/api/v1/intelligence/sentiment/{symbol}`| GET | Get news sentiment time series |
| `/api/v1/intelligence/ml-ranking` | GET | Get ML strategy rankings |

---

## 8. Authentication & Rate Limiting

* **Auth:** API Key authentication for the MVP.
* **Rate Limiting:** IP-based and Key-based rate limits applied at the middleware level to prevent abuse, particularly for expensive LLM or backtest endpoints.
