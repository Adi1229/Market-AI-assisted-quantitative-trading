# 03 — MVP Scope Definition

| Field | Value |
|---|---|
| **Document ID** | MVP-001 |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [PRD](./01_PRODUCT_REQUIREMENTS_DOCUMENT.md), [SRS](./02_SOFTWARE_REQUIREMENTS_SPECIFICATION.md), [Open Questions](./33_OPEN_QUESTIONS.md) |

---

## 1. Purpose

This document explicitly separates features into MVP, Phase 2, and Phase 3. Only features required to demonstrate the core platform belong in the MVP. Future features must not silently become MVP requirements.

---

## 2. Classification Legend

| Tag | Meaning |
|---|---|
| **CLIENT-CONFIRMED** | Feature explicitly required by client |
| **PROPOSED** | Recommended by architecture team; not yet confirmed |
| **ASSUMPTION** | Inferred from context; requires client confirmation |

---

## 3. MVP — Core Platform

### 3.1 Market Data Ingestion

| Feature | Req IDs | Classification |
|---|---|---|
| Provider-agnostic market data interface | FR-MD-001, FR-MD-010 | CLIENT-CONFIRMED |
| Historical market data ingestion | FR-MD-002 | CLIENT-CONFIRMED |
| Indian stocks support | FR-MD-004 | CLIENT-CONFIRMED |
| Major Indian indices support | FR-MD-005 | CLIENT-CONFIRMED |
| Multiple timeframes | FR-MD-006 | CLIENT-CONFIRMED |
| Intraday data | FR-MD-007 | CLIENT-CONFIRMED |
| Persistent storage | FR-MD-009 | CLIENT-CONFIRMED |
| Corporate action handling | FR-MD-013 | CLIENT-CONFIRMED |
| Data validation and deduplication | FR-MD-011, FR-MD-012 | PROPOSED |

### 3.2 Quantitative Feature Engineering

| Feature | Req IDs | Classification |
|---|---|---|
| Modular feature framework | FR-QA-001 | CLIENT-CONFIRMED |
| Feature categories: momentum, trend, volatility, volume, price action, statistical, technical indicators, market regime | FR-QA-002 | CLIENT-CONFIRMED |
| Extensible pipeline (add features without rewrite) | FR-QA-003 | CLIENT-CONFIRMED |
| Feature metadata (lookback, columns, timestamp behavior) | FR-QA-004 | PROPOSED |

### 3.3 Strategy Framework

| Feature | Req IDs | Classification |
|---|---|---|
| Strategy Studio / Registry | FR-SF-001 | CLIENT-CONFIRMED |
| Standardized strategy interface | FR-SF-001 | CLIENT-CONFIRMED |
| Strategy versioning | FR-SF-004 | CLIENT-CONFIRMED |
| Strategy activation/deactivation | FR-SF-005 | CLIENT-CONFIRMED |
| Initial strategies: trend following, momentum, mean reversion, breakout, volatility, statistical | FR-SF-002 | CLIENT-CONFIRMED |
| Configurable parameters | FR-SF-003 | CLIENT-CONFIRMED |

### 3.4 Backtesting Engine

| Feature | Req IDs | Classification |
|---|---|---|
| Performance metrics suite | FR-BT-001 | CLIENT-CONFIRMED |
| Parameter optimization | FR-BT-002 | CLIENT-CONFIRMED |
| Train/test separation | FR-BT-003 | CLIENT-CONFIRMED |
| Out-of-sample validation | FR-BT-004 | CLIENT-CONFIRMED |
| Walk-forward validation | FR-BT-005 | CLIENT-CONFIRMED |
| Anti-bias safeguards (look-ahead, data leakage, survivorship, overfitting, timestamp alignment) | FR-BT-006 to FR-BT-010 | CLIENT-CONFIRMED |
| Configurable transaction costs, slippage, fees | FR-BT-011 | CLIENT-CONFIRMED |
| Reproducible backtests | FR-BT-012 | CLIENT-CONFIRMED |

### 3.5 ML Strategy Selection & Intelligence

| Feature | Req IDs | Classification |
|---|---|---|
| ML-based strategy ranking | FR-ML-001 | CLIENT-CONFIRMED |
| Market condition features | FR-ML-002 | CLIENT-CONFIRMED |
| Strategy-ranking layer (not autonomous trading) | FR-ML-003 | CLIENT-CONFIRMED |
| Time-series validation | FR-ML-004 | CLIENT-CONFIRMED |

### 3.6 Signal Engine & Decision Modes

| Feature | Req IDs | Classification |
|---|---|---|
| Strategy-Only Decision Mode | FR-SE-001 | CLIENT-CONFIRMED |
| AI-Only Decision Mode (Structured Thesis) | FR-SE-002 | CLIENT-CONFIRMED |
| Hybrid Strategy + AI Decision Mode | FR-SE-003 | CLIENT-CONFIRMED |
| Signal Engine orchestrator | FR-SE-004 | CLIENT-CONFIRMED |
| Transparent evidence aggregator | FR-SE-005 | CLIENT-CONFIRMED |
| Standardized Trade Opportunity object | FR-SE-006 | CLIENT-CONFIRMED |

### 3.7 Execution & Risk

| Feature | Req IDs | Classification |
|---|---|---|
| Execution Engine Abstraction | FR-EX-001 | CLIENT-CONFIRMED |
| Paper Trading Simulation | FR-EX-002 | CLIENT-CONFIRMED |
| Virtual Portfolio Tracking | FR-EX-003 | CLIENT-CONFIRMED |
| Dedicated Risk Engine | FR-RE-001 | CLIENT-CONFIRMED |
| Human-in-the-loop Approval Workflow | FR-EX-004 | CLIENT-CONFIRMED |
| Telegram Bot Notifications & Actions | FR-NOT-001 | CLIENT-CONFIRMED |

### 3.8 News & Sentiment

| Feature | Req IDs | Classification |
|---|---|---|
| Financial news ingestion | FR-NS-001 | CLIENT-CONFIRMED |
| NLP sentiment analysis | FR-NS-002 | CLIENT-CONFIRMED |
| Stock-level and index-level sentiment | FR-NS-003, FR-NS-004 | CLIENT-CONFIRMED |
| Sentiment time series | FR-NS-005 | CLIENT-CONFIRMED |
| Provider abstraction | FR-NS-007 | CLIENT-CONFIRMED |
| Publication vs. retrieval time distinction | FR-NS-008 | CLIENT-CONFIRMED |

### 3.9 Fundamental Analysis

| Feature | Req IDs | Classification |
|---|---|---|
| Fundamental metrics | FR-FA-001 | CLIENT-CONFIRMED |
| Replaceable providers | FR-FA-002 | CLIENT-CONFIRMED |
| Point-in-time data handling | FR-FA-003 | CLIENT-CONFIRMED |

### 3.10 AI Market Intelligence Chatbot

| Feature | Req IDs | Classification |
|---|---|---|
| AI chatbot for market Q&A | FR-AI-001 | CLIENT-CONFIRMED |
| Coverage: stocks, indices, market conditions, features, fundamentals, news, sentiment, strategy performance, backtest results | FR-AI-002 | CLIENT-CONFIRMED |
| RAG/vector search where appropriate | FR-AI-003 | CLIENT-CONFIRMED |
| No fabrication of financial data | FR-AI-004 | CLIENT-CONFIRMED |
| Grounded answers for live/current data | FR-AI-005 | CLIENT-CONFIRMED |

### 3.11 Web Dashboard, API & Infrastructure

| Feature | Req IDs | Classification |
|---|---|---|
| Web dashboard | FR-WD-001 | CLIENT-CONFIRMED |
| REST API | FR-WD-002 | CLIENT-CONFIRMED |
| Database infrastructure | FR-IF-001 | CLIENT-CONFIRMED |
| Automated testing | FR-IF-002 | CLIENT-CONFIRMED |

---

## 4. Phase 2 — Future / Gated Execution

> [!NOTE]
> Phase 2 features are important but not required for the initial MVP demonstration.

| Feature | Classification | Dependency |
|---|---|---|
| Live Trading Execution | CLIENT-CONFIRMED | Requires broker integration, gated approval |
| Broker API integration (provider-agnostic) | CLIENT-CONFIRMED | Requires Execution Engine |
| Multi-user authentication (OAuth/SSO) | PROPOSED | Requires auth infrastructure |
| WhatsApp Notification Adapter | CLIENT-CONFIRMED | Requires Notification Service |
| Enhanced ML models (ensemble, neural networks) | PROPOSED | Requires validated ML pipeline |
| Live/near-real-time data streaming | CLIENT-CONFIRMED | Requires infrastructure for streaming |
| Model retraining pipeline | PROPOSED | Requires ML pipeline |

---

## 5. Phase 3 — Production / SaaS Features

> [!NOTE]
> Phase 3 features are long-term capabilities for production SaaS.

| Feature | Classification | Notes |
|---|---|---|
| Fully autonomous real-money trading | CLIENT-CONFIRMED | Explicitly excluded from MVP |
| Multi-tenant SaaS architecture | PROPOSED | Client confirmed SaaS evolution goal |
| Tenant isolation and billing | PROPOSED | Requires tenancy model decision |
| Mobile application | PROPOSED | Explicitly not required for MVP |
| Options/derivatives support | PROPOSED | Explicitly excluded from MVP |

---

## 6. MVP Acceptance Gate

The MVP is considered complete when:

- [ ] All CLIENT-CONFIRMED MVP features (including Paper Trading and Telegram) are implemented and tested
- [ ] The three independent Decision Modes (Strategy-Only, AI-Only, Hybrid) function correctly
- [ ] Backtesting produces reproducible results independent of live execution
- [ ] Anti-bias safeguards pass automated tests
- [ ] Web dashboard displays all core data and results
- [ ] REST API is documented and functional

See [34_ACCEPTANCE_CRITERIA.md](./34_ACCEPTANCE_CRITERIA.md) for detailed acceptance criteria.
