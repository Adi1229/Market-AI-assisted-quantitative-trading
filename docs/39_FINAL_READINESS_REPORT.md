# 39 — Final Implementation-Readiness Report

| Field | Value |
|---|---|
| **Document ID** | RDY-001 |
| **Version** | 1.0.0-final |
| **Status** | Approved |
| **Last Updated** | 2026-08-15 |

---

## 1. Final MVP Scope
The MVP is explicitly a research, backtesting, and paper-trading platform with human-in-the-loop approval. It includes:
* Market data ingestion (historical & intraday for Indian equities/indices).
* Quantitative feature engineering.
* Strategy Studio (creation, versioning, backtesting of modular strategies).
* ML strategy ranking.
* AI market intelligence (RAG Chatbot + structured Decision Engine).
* Signal Engine (Strategy-Only, AI-Only, Hybrid decision modes).
* Dedicated Risk Engine (Max position, daily loss, stale signals).
* Notification Service (Telegram Bot for trade approval).
* Execution Engine (Paper Trading with a virtual portfolio).
* Web Dashboard & REST API.

## 2. Explicitly OUT of MVP
* Fully autonomous real-money trading (no unsupervised execution).
* Live broker integration (gated for Phase 2).
* High-frequency trading (HFT) / microsecond latency.
* Complex derivatives (options/futures).
* Multi-tenant SaaS billing.
* Mobile application.
* WhatsApp integration.
* Large-scale distributed infrastructure.

## 3. Final Architecture
A modular, microservices-inspired monolithic architecture built on FastAPI, Next.js, and PostgreSQL+TimescaleDB. The architecture strictly decouples Data Ingestion, Feature Computation, Decision Generation, Risk Management, User Approval, and Execution into isolated layers.

## 4. Final Project Structure
```text
backend/
├── app/
│   ├── api/                # REST endpoints
│   ├── core/               # Signal Engine, Risk Engine, Execution Engine (Paper)
│   ├── data/               # Ingestion, Providers, Database
│   ├── features/           # Quantitative features
│   ├── strategies/         # Strategy Studio registry
│   ├── intelligence/       # AI Decision Engine, Chatbot, ML Ranking
│   ├── backtesting/        # Historical Simulation
│   └── notifications/      # Telegram integration
frontend/
└── src/app/                # Next.js Dashboard
```

## 5. Decision Modes
Orchestrated by the **Signal Engine**:
1. **Strategy-Only:** Strategy Engine generates signals; AI provides informational context only.
2. **AI-Only:** AI Decision Engine generates a structured trade thesis; no strategy required.
3. **Hybrid Strategy + AI:** Independent Strategy and AI evaluations combined via a deterministic Decision Aggregator preserving distinct scores.

## 6. Execution Modes
Orchestrated by the **Execution Engine**:
1. **Backtest:** Historical vectorized signal generation with event-driven execution simulation. Completely isolated from active trading.
2. **Paper (MVP):** Simulated execution of active signals on real-time data against a virtual portfolio.
3. **Live (Future):** Real broker execution. Disabled by default, gated behind risk checks and a kill switch.

## 7. Strategy Studio Design
A plugin-style architecture where strategies are modular Python classes implementing `BaseStrategy`. They declare metadata, parameters, and required features, generating standardized `StrategySignal` objects. Strategies are versioned, independently testable, and have explicit statuses (`ACTIVE`, `INACTIVE`).

## 8. Signal Engine Design
The central orchestrator that consumes outputs from the Strategy Engine, AI Engine, and Market Intelligence. It applies the active Decision Mode logic and produces standardized `TradeOpportunity` objects (containing identity, mode, direction, scores, reasoning, and data references).

## 9. Risk Engine Design
A strict gatekeeper sitting between the Signal Engine and User Approval. It evaluates every `TradeOpportunity` against portfolio exposure, max position sizes, daily loss limits, and signal staleness. Failed opportunities are logged and rejected; they never reach execution.

## 10. Paper Trading Design
Simulates execution by consuming `TradeOpportunity` objects and generating `Order` objects filled at the next available price. Updates a `VirtualPortfolio` state (tracking unrealized/realized P&L, exposure, and drawdown). Implements the abstract `ExecutionProvider` interface.

## 11. Telegram Workflow
A stateless notification and action channel. The Notification Service sends a formatted message with Strategy/AI evidence. The user clicks `TAKE_TRADE` or `IGNORE`. The Telegram Bot routes the action back to the backend API. It contains absolutely zero business or trading logic.

## 12. Future Broker Integration Boundary
Live broker execution will implement the same `ExecutionProvider` interface used by Paper Trading. The execution engine router will simply direct approved trades to the `BrokerProvider` instead of the `PaperProvider` based on configuration, requiring zero changes to the Strategy, Signal, or Risk engines.

## 13. Phase-by-Phase Implementation Order
1. **Foundation & Data Layer:** DB schema, Market Data ingestion.
2. **Quantitative Engine & Strategy Studio:** Features, Strategy registry.
3. **Backtesting & Validation:** Engine, metrics, optimization.
4. **Intelligence & ML Layer:** Sentiment, Fundamentals, AI Decision, Chatbot.
5. **Decision, Risk & Execution (MVP Core):** Signal Engine, Risk Engine, Telegram, Paper Trading.
6. **Frontend Dashboard:** Next.js UI integration.

## 14. Critical Assumptions
* DhanHQ or equivalent will be the eventual Phase 2 broker.
* TimescaleDB fits MVP scale requirements for time-series data.
* Commercial LLM APIs (OpenAI/Anthropic) are acceptable for MVP before moving to self-hosted for privacy if needed.

## 15. Remaining Open Questions
* Exact provider selections (Market Data, News, Fundamentals, LLM). (Mitigation: Abstracted behind interfaces; mock providers used for initial development).

---

## Consistency Check & Architectural Invariants

### Verification of Dimensions
* **Strategy Only vs AI Only vs Hybrid:** Fully isolated via Signal Engine modes. AI cannot override strategy in Strategy-Only mode. Hybrid transparently aggregates.
* **Backtest vs Paper vs Live:** Completely decoupled. Backtest is a separate simulation engine. Paper and Live share the `ExecutionProvider` interface. Decision modes matrix cleanly with execution modes.
* **Strategy Engine vs AI Engine:** Strictly separate code paths. They do not depend on each other.
* **Signal Engine vs Risk Engine:** Signal Engine creates opportunities; Risk Engine validates them. Clean boundary.
* **Risk Engine vs Execution Engine:** Execution Engine only receives opportunities that have passed the Risk Engine and User Approval.
* **Paper vs Broker execution:** Both implement identical abstract methods (`place_order`, `get_positions`).
* **Strategy versioning:** Enforced in `metadata.json` and tracked in `TradeOpportunity` and Backtest logs.
* **Backtest reproducibility:** Guaranteed by logging `dataset_version`, `strategy_version`, and parameter sets.
* **Look-ahead bias & Data leakage:** Prevented by strict temporal indexing, execution delay (T+1), and purged/walk-forward cross-validation.
* **Point-in-time data:** Fundamentals use `availability_date`; News uses `publication_time`.
* **Human approval:** Centralized in the Notification Service via Telegram before the Execution Engine is invoked.

### Non-Negotiable Architecture Constraints
1. **Strategy Engine must not depend on the AI Engine.**
2. **AI Engine must not modify or override a Strategy signal in STRATEGY_ONLY mode.**
3. **Strategy Engine must not directly execute trades.**
4. **AI Engine must not directly execute trades.**
5. **Signal Engine produces standardized TradeOpportunity objects.**
6. **Risk Engine must sit between Decision/Signal and Execution.**
7. **Execution Engine must not contain strategy logic.**
8. **Telegram must not contain trading/business logic.** (Telegram is only a notification/action interface).
9. **Paper execution and broker execution must use the execution abstraction.**
10. **Backtesting must remain isolated from live execution.**
11. **Every strategy must implement the standardized strategy interface.**
12. **Every strategy must be independently testable.**
13. **Strategy versions and parameters must be recorded for reproducibility.**
14. **All trade opportunities must be auditable.**
15. **Live trading must be disabled by default.**
16. **No external provider may be directly coupled to core business logic.**
17. **Provider-specific code must live behind provider interfaces/adapters.**
18. **AI-generated financial claims must be grounded in available data.**
19. **Never fabricate market data, news, fundamentals, prices, or backtest results.**
20. **Do not introduce a new framework or architectural pattern without documenting why it is necessary.**

### Contradictions Remaining
> **None.** The decoupling of Decision Modes (Signal Engine) from Execution Modes (Execution Engine) resolves previous ambiguity regarding Paper Trading and Strategy/AI separation. No contradictions were found during the final review.

---
**Status:** The documentation suite is finalized and frozen. The platform architecture is coherent, safe, and ready for implementation.
