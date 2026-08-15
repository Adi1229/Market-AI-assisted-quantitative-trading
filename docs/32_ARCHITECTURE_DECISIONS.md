# 32 — Architecture Decisions (ADRs)

| Field | Value |
|---|---|
| **Document ID** | ADR-INDEX |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |

---

## Index of Decisions

1. [ADR-001: PostgreSQL + TimescaleDB for All Data](#adr-001-postgresql--timescaledb-for-all-data)
2. [ADR-002: FastAPI for Backend Framework](#adr-002-fastapi-for-backend-framework)
3. [ADR-003: Next.js / React for Frontend](#adr-003-nextjs--react-for-frontend)
4. [ADR-004: Provider-Agnostic Interfaces](#adr-004-provider-agnostic-interfaces)
5. [ADR-005: pgvector for MVP Vector Store](#adr-005-pgvector-for-mvp-vector-store)
6. [ADR-006: Hybrid Backtesting Engine](#adr-006-hybrid-backtesting-engine)
7. [ADR-007: LightGBM for Strategy Ranking](#adr-007-lightgbm-for-strategy-ranking)
8. [ADR-008: Publication vs Retrieval Timestamps](#adr-008-publication-vs-retrieval-timestamps)
9. [ADR-009: Redis for Caching and Task Queue](#adr-009-redis-for-caching-and-task-queue)
10. [ADR-010: AWS ECS Fargate for MVP Deployment](#adr-010-aws-ecs-fargate-for-mvp-deployment)
11. [ADR-011: Strict Separation of Decision and Execution Modes](#adr-011-strict-separation-of-decision-and-execution-modes) (NEW)

---

## ADR-011: Strict Separation of Decision and Execution Modes

**Date:** 2026-08-15
**Status:** Accepted (Client-Confirmed)

### Context
The platform must support different ways of generating trade ideas (Strategy, AI, Hybrid) and different ways of executing them (Backtest, Paper, Live). Combining these into a single engine creates a monolithic, fragile system where adding a new execution mode requires rewriting decision logic.

### Decision
We will enforce a strict architectural separation:
1. **Decision Modes (`STRATEGY_ONLY`, `AI_ONLY`, `HYBRID`)** are managed exclusively by the **Signal Engine**, which produces a standardized `TradeOpportunity`.
2. **Execution Modes (`BACKTEST`, `PAPER`, `LIVE`)** are managed independently. The Execution Engine consumes the `TradeOpportunity` via an abstract `ExecutionProvider` interface.

### Consequences
* **Positive:** Decision modes and execution modes are matrixed; any combination is valid (e.g., Hybrid Decision + Paper Execution).
* **Positive:** Adding broker integrations later requires zero changes to the strategy or AI code.
* **Positive:** Testing the AI decision logic does not require simulating broker fills.
* **Negative:** Requires creating mapping layers (standardized opportunity and order objects) between the sub-systems, increasing initial development time slightly.
