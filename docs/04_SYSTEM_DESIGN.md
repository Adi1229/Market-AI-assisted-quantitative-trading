# 04 — System Design

| Field | Value |
|---|---|
| **Document ID** | SD-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Architecture](./05_ARCHITECTURE.md), [Data Architecture](./06_DATA_ARCHITECTURE.md), [PRD](./01_PRODUCT_REQUIREMENTS_DOCUMENT.md) |

---

## 1. System Overview

The platform is a layered system for quantitative research and market intelligence on Indian equities. It is designed as a **research-first** platform — the MVP is strictly research and backtesting, with no live execution.

```mermaid
graph TB
    subgraph "Presentation Layer"
        FE["Web Dashboard<br/>(React/Next.js)"]
    end

    subgraph "API Layer"
        API["REST API<br/>(FastAPI)"]
    end

    subgraph "Application Services"
        MD["Market Data<br/>Service"]
        FEng["Feature Engineering<br/>Service"]
        ST["Strategy<br/>Service"]
        BT["Backtesting<br/>Engine"]
        ML["ML Strategy<br/>Ranking"]
        NS["News & Sentiment<br/>Service"]
        FA["Fundamental<br/>Analysis Service"]
        CB["AI Chatbot<br/>Service"]
    end

    subgraph "Data Access Layer"
        DAL["Data Access<br/>Layer"]
    end

    subgraph "External Providers"
        MDP["Market Data<br/>Provider (TBD)"]
        NP["News<br/>Provider (TBD)"]
        FDP["Fundamental Data<br/>Provider (TBD)"]
        LLM["LLM<br/>Provider (TBD)"]
    end

    subgraph "Storage Layer"
        PG["PostgreSQL /<br/>TimescaleDB"]
        RD["Redis<br/>(Cache)"]
        VS["Vector Store<br/>(TBD)"]
    end

    FE --> API
    API --> MD & FEng & ST & BT & ML & NS & FA & CB
    MD --> DAL & MDP
    FEng --> DAL
    ST --> DAL
    BT --> DAL & FEng & ST
    ML --> DAL & BT
    NS --> DAL & NP
    FA --> DAL & FDP
    CB --> DAL & LLM & VS
    DAL --> PG & RD
```

---

## 2. Design Principles

| Principle | Description |
|---|---|
| **Provider Agnosticism** | All external providers are abstracted behind interfaces (CLIENT-CONFIRMED) |
| **Research First** | MVP is research/backtesting only; no live execution (CLIENT-CONFIRMED) |
| **Temporal Integrity** | All data access respects temporal boundaries to prevent look-ahead bias (CLIENT-CONFIRMED) |
| **Modularity** | Features, strategies, and providers are pluggable (CLIENT-CONFIRMED) |
| **Reproducibility** | All backtests must be reproducible (CLIENT-CONFIRMED) |
| **No Fabrication** | AI chatbot must never invent financial data (CLIENT-CONFIRMED) |
| **SaaS-Ready Architecture** | Design decisions should not preclude future multi-tenancy (CLIENT-CONFIRMED) |
| **MVP Minimalism** | Do not over-engineer the MVP (CLIENT-CONFIRMED) |

---

## 3. Layered Architecture

### 3.1 Presentation Layer

| Component | Technology | Responsibility |
|---|---|---|
| Web Dashboard | React/Next.js (client preference) | Interactive data visualization, strategy management, backtest results, chatbot |

### 3.2 API Layer

| Component | Technology | Responsibility |
|---|---|---|
| REST API | FastAPI (client preference) | Versioned HTTP endpoints; request validation; authentication; rate limiting |

### 3.3 Application Services Layer

| Service | Responsibility |
|---|---|
| Market Data Service | Data ingestion, validation, corporate action handling |
| Feature Engineering Service | Modular feature computation, feature registry |
| Strategy Service | Strategy management, signal generation, parameter handling |
| Backtesting Engine | Historical simulation, performance metrics, optimization |
| ML Strategy Ranking | Strategy ranking based on market conditions |
| News & Sentiment Service | News ingestion, NLP sentiment, entity recognition |
| Fundamental Analysis Service | Fundamental data ingestion, point-in-time queries |
| AI Chatbot Service | Query understanding, retrieval, grounded response generation |

### 3.4 Data Access Layer

| Component | Responsibility |
|---|---|
| Repository Pattern | Abstract database access; prevent SQL coupling in services |
| Query Builders | Temporal queries (as-of date); time-series aggregation |
| Cache Layer | Redis-backed caching for frequently accessed data |

### 3.5 Storage Layer

| Component | Technology | Use Case |
|---|---|---|
| Primary Database | PostgreSQL + TimescaleDB (client preference) | OHLCV time-series, metadata, backtest results |
| Cache | Redis (client preference, where justified) | Session cache, computed feature cache, rate limiting |
| Vector Store | TBD (pgvector recommended for MVP) | AI chatbot context retrieval |

### 3.6 External Provider Layer

| Provider Type | Status | Abstraction |
|---|---|---|
| Market Data | TBD (DhanHQ candidate) | `MarketDataProvider` interface |
| News | TBD | `NewsProvider` interface |
| Fundamental Data | TBD | `FundamentalDataProvider` interface |
| LLM | TBD | `LLMProvider` interface |
| Broker | Phase 2+ | `BrokerProvider` interface |

---

## 4. Data Flow

### 4.1 Data Ingestion Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant MDS as Market Data Service
    participant Provider as Market Data Provider
    participant Validator as Data Validator
    participant DB as PostgreSQL/TimescaleDB

    Scheduler->>MDS: Trigger ingestion (instrument, timeframe, date range)
    MDS->>Provider: Request historical data
    Provider-->>MDS: Raw OHLCV data
    MDS->>Validator: Validate data
    Validator-->>MDS: Validation report
    alt Valid Data
        MDS->>DB: Upsert OHLCV records
        MDS->>DB: Log ingestion metadata
    else Invalid Data
        MDS->>DB: Log validation errors
        MDS->>MDS: Handle errors (retry/flag/skip)
    end
```

### 4.2 Backtesting Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant BT as Backtesting Engine
    participant FE as Feature Engine
    participant ST as Strategy
    participant PM as Portfolio Manager
    participant DB as Database

    User->>API: Run backtest (strategy, params, instruments, date range)
    API->>BT: Initialize backtest
    BT->>DB: Load OHLCV data (date range)
    BT->>FE: Compute features
    FE-->>BT: Data with features
    BT->>ST: Generate signals (in-sample only if optimizing)
    ST-->>BT: Trading signals
    BT->>PM: Simulate portfolio (signals, costs, slippage)
    PM-->>BT: Trade history, equity curve
    BT->>BT: Calculate performance metrics
    BT->>DB: Store backtest run + results + metadata
    BT-->>API: Backtest results
    API-->>User: Results + metrics
```

### 4.3 AI Chatbot Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant CB as Chatbot Service
    participant QU as Query Understanding
    participant RT as Retriever
    participant DB as Database/Vector Store
    participant LLM as LLM Provider

    User->>API: Ask question
    API->>CB: Process query
    CB->>QU: Classify intent & extract entities
    QU-->>CB: Intent, entities, data requirements
    CB->>RT: Retrieve relevant data
    RT->>DB: Query structured data + vector search
    DB-->>RT: Retrieved context
    RT-->>CB: Ranked context
    CB->>LLM: Generate response (question + context)
    LLM-->>CB: Draft response
    CB->>CB: Verify grounding (no fabricated data)
    CB-->>API: Grounded response with sources
    API-->>User: Answer
```

---

## 5. Key Design Decisions

| Decision | Choice | Rationale | See Also |
|---|---|---|---|
| Backtesting engine type | Hybrid (vectorized + event hooks) | Balance of performance and flexibility | [ADR-006](./32_ARCHITECTURE_DECISIONS.md) |
| Database | PostgreSQL + TimescaleDB | Client preference; time-series optimization | [ADR-001](./32_ARCHITECTURE_DECISIONS.md) |
| Vector store (MVP) | pgvector (recommended) | Reduces infrastructure; sufficient at MVP scale | [ADR-005](./32_ARCHITECTURE_DECISIONS.md) |
| ML models | Start with gradient boosting | Tabular data; interpretable; fast iteration | [ADR-007](./32_ARCHITECTURE_DECISIONS.md) |
| Provider abstraction | Interface-based | Client requirement; enables provider replacement | [25_DATA_PROVIDER_ABSTRACTION.md](./25_DATA_PROVIDER_ABSTRACTION.md) |

---

## 6. Scalability Considerations (Future)

> [!NOTE]
> These are architectural notes for future SaaS evolution, not MVP requirements.

| Dimension | MVP Approach | Future Scale |
|---|---|---|
| Users | Single user (assumption) | Multi-tenant with isolation |
| Data volume | Hundreds of instruments | Thousands of instruments |
| Compute | Single-server backtesting | Distributed backtesting workers |
| Real-time | Polling / delayed data | WebSocket streaming |
| ML inference | Batch | Near-real-time |

---

## 7. Cross-References

| Document | Relevance |
|---|---|
| [Architecture](./05_ARCHITECTURE.md) | Detailed component architecture |
| [Data Architecture](./06_DATA_ARCHITECTURE.md) | Data flow and lineage |
| [Database Design](./08_DATABASE_DESIGN.md) | Schema and storage |
| [Provider Abstraction](./25_DATA_PROVIDER_ABSTRACTION.md) | External provider interfaces |
| [Deployment Architecture](./22_DEPLOYMENT_ARCHITECTURE.md) | Infrastructure and deployment |
