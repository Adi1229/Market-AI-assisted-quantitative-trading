# 28 — Project Structure

| Field | Value |
|---|---|
| **Document ID** | PS-001 |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Architecture](./05_ARCHITECTURE.md), [Implementation Plan](./29_IMPLEMENTATION_PLAN.md) |

---

## 1. Top-Level Repository Structure

```text
market_2.0/
├── backend/            # FastAPI application and quant engines
├── frontend/           # Next.js web dashboard
├── docs/               # Documentation suite (these files)
├── scripts/            # Deployment and utility scripts
├── .github/            # CI/CD workflows
├── docker-compose.yml  # Local dev orchestration
└── README.md
```

---

## 2. Backend Directory Structure (Python)

The backend is structured by domain components to reflect the strict separation between Data, Decision, Risk, and Execution.

```text
backend/
├── app/
│   ├── main.py                     # FastAPI application entry point
│   │
│   ├── api/                        # REST API Routes
│   │   ├── v1/
│   │   │   ├── instruments.py
│   │   │   ├── data.py
│   │   │   ├── strategies.py
│   │   │   ├── signal_engine.py
│   │   │   ├── execution.py
│   │   │   ├── portfolio.py
│   │   │   ├── backtest.py
│   │   │   └── chat.py
│   │   └── dependencies.py         # Auth and DB injection
│   │
│   ├── core/                       # Core engine abstractions
│   │   ├── signal_engine/          # Orchestrates Decision Modes
│   │   │   ├── aggregator.py       # Hybrid decision scoring
│   │   │   └── opportunity.py      # TradeOpportunity object
│   │   ├── risk_engine/            # Gates execution
│   │   │   └── rules.py            # Max position, daily loss, etc.
│   │   ├── execution_engine/       # Execution abstraction
│   │   │   ├── base.py             # ExecutionProvider interface
│   │   │   ├── paper_trading.py    # Paper execution simulation
│   │   │   └── portfolio.py        # Virtual portfolio state
│   │   ├── config.py               # Settings (Pydantic)
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── data/                       # Data layer
│   │   ├── ingestion/              # Orchestration
│   │   ├── providers/              # Provider implementations
│   │   │   ├── base.py             # Provider-agnostic interfaces
│   │   │   ├── dhan.py             # (Candidate) Market Data
│   │   │   └── mock.py             # Mock providers for testing
│   │   └── database/               # PostgreSQL / TimescaleDB
│   │       ├── models.py           # SQLAlchemy / SQLModel
│   │       ├── repository.py
│   │       └── migrations/         # Alembic
│   │
│   ├── features/                   # Quantitative Feature Engine
│   │   ├── base.py                 # Feature interface
│   │   ├── registry.py
│   │   ├── momentum.py
│   │   └── volatility.py
│   │
│   ├── strategies/                 # Strategy Studio (Plugin structure)
│   │   ├── base.py                 # Strategy interface
│   │   ├── registry.py
│   │   ├── strategy_001_momentum/
│   │   │   ├── strategy.py
│   │   │   ├── config.yaml
│   │   │   └── metadata.json
│   │   └── strategy_002_mean_revert/
│   │
│   ├── intelligence/               # AI & ML Layer
│   │   ├── decision_engine/        # AI structured trade thesis generator
│   │   ├── chatbot/                # Conversational AI (RAG)
│   │   ├── sentiment/              # NLP processors
│   │   ├── fundamentals/           # Fundamental analysis
│   │   ├── ml_ranking/             # ML strategy selection
│   │   └── llm_providers/          # Abstraction for OpenAI/Anthropic
│   │
│   ├── backtesting/                # Historical Simulation Engine
│   │   ├── engine.py               # Event loop / Vectorized engine
│   │   ├── metrics.py              # Performance calculations
│   │   └── optimization.py         # Parameter optimization
│   │
│   └── notifications/              # Human-in-the-loop Notification
│       ├── base.py                 # NotificationAdapter interface
│       ├── telegram_bot.py         # Telegram integration
│       └── web_notifier.py         # Dashboard notifications
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── requirements.txt
└── pyproject.toml
```

---

## 3. Frontend Directory Structure (Next.js)

```text
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── dashboard/          # Main dashboard overview
│   │   ├── instruments/        # Market data explorer
│   │   ├── strategies/         # Strategy Studio UI
│   │   ├── opportunities/      # Signal Engine output (Approve/Reject)
│   │   ├── portfolio/          # Paper Trading / Live Portfolio view
│   │   ├── backtests/          # Backtest runner and reports
│   │   ├── intelligence/       # AI Chatbot interface
│   │   └── settings/           # Config (Execution Mode, Risk Limits)
│   │
│   ├── components/
│   │   ├── charts/             # TradingView Lightweight Charts
│   │   ├── ui/                 # Reusable UI components (Tailwind/Radix)
│   │   └── chat/               # Chatbot UI
│   │
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   └── utils.ts
│   │
│   └── hooks/                  # React queries and state
│
├── package.json
└── tailwind.config.js
```

---

## 4. Key Architectural Enforcements

1. **Circular Dependencies:** 
   * `strategies` can import `features` but NOT vice-versa.
   * `signal_engine` imports `strategies` and `intelligence`, but they do not import `signal_engine`.
   * `execution_engine` imports nothing from `strategies` or `signal_engine` (it only executes approved `TradeOpportunity` objects).
2. **Provider Isolation:** All external API logic lives exclusively inside `data/providers/`, `intelligence/llm_providers/`, or `notifications/`.

---

## 5. Cross-References

| Document | Relevance |
|---|---|
| [Architecture](./05_ARCHITECTURE.md) | High-level component definitions |
| [Coding Guidelines](./27_CODING_GUIDELINES.md) | Python/React stylistic rules |
