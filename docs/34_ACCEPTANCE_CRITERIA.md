# 34 — Acceptance Criteria

| Field | Value |
|---|---|
| **Document ID** | AC-001 |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [SRS](./02_SOFTWARE_REQUIREMENTS_SPECIFICATION.md), [MVP Scope](./03_MVP_SCOPE.md), [Testing Strategy](./20_TESTING_STRATEGY.md) |

---

## 1. Core Platform (Data & Features)

| ID | Criterion | Verification |
|---|---|---|
| AC-MD-001 | Historical OHLCV data can be ingested for configured instruments | Run ingestion; verify data in database |
| AC-MD-002 | Data timestamps are validated | Ingest data with known violations; verify detection |
| AC-FE-001 | A new feature can be added without modifying existing pipeline code | Add feature class; verify pipeline discovers it |
| AC-FE-002 | Feature values at time T are identical whether future data exists or not | Truncation test: compute on [0,T] vs [0,T+N] |

---

## 2. Strategy Studio & Backtesting

| ID | Criterion | Verification |
|---|---|---|
| AC-SF-001 | Strategies can be activated/deactivated via registry | Change status; verify Signal Engine behavior |
| AC-SF-002 | Parameters can be modified without code changes | Change parameters; verify different signals |
| AC-BT-001 | Same inputs produce identical, reproducible results | Run same backtest twice; compare all metrics |
| AC-BT-002 | Train/test periods are non-overlapping in optimization | Verify no data from test period in training |
| AC-BT-003 | Signal at time T is executed at > T | Inspect trade records; verify execution time |

---

## 3. Signal Engine & Decision Modes (NEW)

| ID | Criterion | Verification |
|---|---|---|
| AC-SIG-001 | STRATEGY_ONLY mode generates opportunities based solely on strategy | Run mode; verify AI evidence is empty |
| AC-SIG-002 | AI_ONLY mode generates structured trade theses | Run mode; verify output is valid JSON thesis |
| AC-SIG-003 | HYBRID mode preserves individual strategy and AI scores | Run mode; inspect opportunity object |
| AC-SIG-004 | Decision Aggregator calculates combined score correctly | Pass known fixed inputs; verify math |
| AC-SIG-005 | Every opportunity logs full evidence for auditability | Query DB; verify all metadata fields |

---

## 4. Execution, Risk & Notifications (NEW)

| ID | Criterion | Verification |
|---|---|---|
| AC-EXE-001 | Risk Engine blocks trades exceeding max position size | Submit oversized trade; verify rejection |
| AC-EXE-002 | Risk Engine blocks stale signals | Submit old signal; verify rejection |
| AC-EXE-003 | Opportunity requires User Approval via Telegram | Generate signal; verify it blocks until Telegram TAKE_TRADE |
| AC-EXE-004 | Paper trading simulates execution and updates virtual portfolio | Approve trade; verify P&L and positions |
| AC-EXE-005 | Live trading is disabled by default | Verify system boots with execution_mode = PAPER |

---

## 5. Intelligence & AI

| ID | Criterion | Verification |
|---|---|---|
| AC-AI-001 | Chatbot answers questions about stocks, features, and backtests | Ask test questions; verify relevant answers |
| AC-AI-002 | Financial data in responses is grounded in retrieved data | Extract numbers from response; verify against context |
| AC-AI-003 | The system does not fabricate prices, returns, or metrics | Ask about non-existent instrument; verify "data not available" response |
| AC-ML-001 | ML model produces strategy rankings without look-ahead | Temporal leakage test passes |

---

## 6. Infrastructure

| ID | Criterion | Verification |
|---|---|---|
| AC-IF-001 | Application can be started with Docker Compose | `docker-compose up`; verify access |
| AC-IF-002 | Automated test suite passes | CI pipeline green |
