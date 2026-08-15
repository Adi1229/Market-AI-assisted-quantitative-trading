# 30 — Tasks

| Field | Value |
|---|---|
| **Document ID** | TASKS-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Implementation Plan](./29_IMPLEMENTATION_PLAN.md), [MVP Scope](./03_MVP_SCOPE.md) |

---

## Phase 0: Documentation
- [x] Analyze client requirements
- [x] Generate 35 documentation files
- [x] Cross-document consistency audit
- [ ] Client review and approval

## Phase 1: Project Foundation
- [ ] Initialize Python project (pyproject.toml, requirements.txt, .gitignore)
- [ ] Create `core/` module (config, models, interfaces, exceptions, enums)
- [ ] Set up database connection management (async)
- [ ] Set up Alembic migrations
- [ ] Create initial schema migration (instruments, ohlcv_data tables)
- [ ] Create Docker Compose for local dev (PostgreSQL+TimescaleDB, Redis)
- [ ] Set up pytest with conftest.py and fixtures
- [ ] Set up linting (ruff, black, isort) in pyproject.toml
- [ ] Create .env.example with all required variables
- [ ] Create README.md with setup instructions

## Phase 2: Market Data Abstraction
- [ ] Implement `MarketDataProvider` abstract interface
- [ ] Implement `Instrument`, `OHLCVRecord`, `CorporateAction` models
- [ ] Implement `MockMarketDataProvider` with sample data
- [ ] Implement provider factory
- [ ] Implement first real provider adapter (provider TBD)
- [ ] Write unit tests for provider interface

## Phase 3: Data Ingestion
- [ ] Implement data ingestion pipeline
- [ ] Implement OHLCV data validation rules (V-001 through V-010)
- [ ] Implement corporate action handling
- [ ] Implement `InstrumentRepository` (CRUD)
- [ ] Implement `OHLCVRepository` (upsert, range query, as-of query)
- [ ] Implement ingestion run tracking
- [ ] Write ingestion integration tests
- [ ] Create CLI script for data ingestion

## Phase 4: Full Database Schema
- [ ] Create all remaining schema migrations
- [ ] Configure TimescaleDB hypertables
- [ ] Create all indexes
- [ ] Implement all repository classes
- [ ] Write repository integration tests
- [ ] Set up pgvector extension (if RAG approach is adopted)

## Phase 5: Feature Engineering
- [ ] Implement `BaseFeature` and `FeatureMetadata`
- [ ] Implement `FeatureRegistry`
- [ ] Implement feature computation pipeline (with lookback buffer)
- [ ] Implement SMA, EMA, MACD, ADX (trend)
- [ ] Implement RSI, Stochastic, ROC (momentum)
- [ ] Implement ATR, Bollinger Bands, Historical Vol (volatility)
- [ ] Implement OBV, VWAP, Volume Ratio (volume)
- [ ] Implement price action features
- [ ] Implement Z-Score, Hurst (statistical)
- [ ] Implement regime detection features
- [ ] Write unit tests for each feature
- [ ] Write look-ahead bias tests for feature computation

## Phase 6: Strategy Framework
- [ ] Implement `BaseStrategy` and `StrategyRegistry`
- [ ] Implement `ParameterSpec` and parameter validation
- [ ] Implement MA Crossover strategy
- [ ] Implement RSI Momentum strategy
- [ ] Implement Bollinger Mean Reversion strategy
- [ ] Implement Donchian Breakout strategy
- [ ] Implement Volatility Regime strategy
- [ ] Implement Z-Score Reversion strategy
- [ ] Write unit tests for each strategy

## Phase 7: Backtesting Engine
- [ ] Implement backtest engine core (hybrid architecture)
- [ ] Implement portfolio manager (cash, positions, equity tracking)
- [ ] Implement order simulator with execution delay
- [ ] Implement Indian market transaction cost model
- [ ] Implement position sizing methods (equal_weight, fixed, percent_risk)
- [ ] Implement stop-loss and take-profit
- [ ] Write backtest correctness tests

## Phase 8: Performance Analytics
- [ ] Implement all required performance metrics
- [ ] Implement benchmark comparison
- [ ] Implement drawdown analysis
- [ ] Implement grid search parameter optimization
- [ ] Implement train/test split enforcement
- [ ] Implement walk-forward validation
- [ ] Implement reproducibility metadata recording
- [ ] Write metrics validation tests (known-answer tests)

## Phase 9: ML Strategy Ranking
- [ ] Implement ML feature engineering (market condition features)
- [ ] Implement training dataset construction
- [ ] Implement time-series cross-validation
- [ ] Implement LightGBM/XGBoost strategy ranker
- [ ] Implement baseline models (Logistic Regression, Random Forest)
- [ ] Implement model evaluation and comparison
- [ ] Implement model registry
- [ ] Write ML pipeline tests (including temporal leakage tests)

## Phase 10: News & Sentiment
- [ ] Implement `NewsProvider` interface and mock
- [ ] Implement news ingestion pipeline
- [ ] Implement deduplication
- [ ] Implement entity recognition / stock mapping
- [ ] Implement sentiment analysis (FinBERT or equivalent)
- [ ] Implement sentiment aggregation (daily, rolling)
- [ ] Implement sentiment features for feature engine
- [ ] Write sentiment pipeline tests

## Phase 11: Fundamentals
- [ ] Implement `FundamentalDataProvider` interface and mock
- [ ] Implement fundamental data ingestion
- [ ] Implement data normalization
- [ ] Implement point-in-time query support
- [ ] Write fundamental data tests (including point-in-time tests)

## Phase 12: AI Chatbot
- [ ] Implement `LLMProvider` interface and mock
- [ ] Implement query understanding (intent + entity extraction)
- [ ] Implement structured data retriever
- [ ] Implement embedding pipeline (if RAG is adopted)
- [ ] Implement vector search (if RAG is adopted)
- [ ] Implement context builder
- [ ] Implement grounding verification
- [ ] Implement chat session management
- [ ] Write chatbot tests (grounding, intent, relevance)

## Phase 13: FastAPI
- [ ] Set up FastAPI application structure
- [ ] Implement authentication middleware
- [ ] Implement rate limiting
- [ ] Implement all API routers (instruments, market data, features, strategies, backtests, ML, sentiment, fundamentals, chat, health)
- [ ] Implement OpenAPI documentation
- [ ] Write API integration tests

## Phase 14: Frontend Dashboard
- [ ] Initialize Next.js project
- [ ] Implement layout, navigation, and design system
- [ ] Implement dashboard overview page
- [ ] Implement instrument browser and detail pages
- [ ] Implement OHLCV candlestick chart
- [ ] Implement strategy management pages
- [ ] Implement backtest configuration and results
- [ ] Implement ML rankings page
- [ ] Implement sentiment dashboard
- [ ] Implement fundamentals page
- [ ] Implement chat interface

## Phase 15: Testing
- [ ] Complete quantitative correctness test suite
- [ ] Complete integration test suite
- [ ] Perform performance testing
- [ ] Perform security testing
- [ ] Perform end-to-end testing
- [ ] Achieve coverage targets

## Phase 16: Deployment
- [ ] Finalize Dockerfiles (backend, frontend, worker)
- [ ] Set up CI/CD pipeline
- [ ] Configure AWS infrastructure (or alternative)
- [ ] Deploy to staging
- [ ] Run staging verification
- [ ] Deploy to production
- [ ] Set up monitoring and alerting
- [ ] Document operational procedures
