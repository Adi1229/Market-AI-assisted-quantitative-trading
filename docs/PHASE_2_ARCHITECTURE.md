# Phase 2 Architecture: Quantitative Engine & Strategy Studio

## Overview
Phase 2 establishes a reusable quantitative framework for feature engineering and strategy execution. It introduces a modular mechanism for processing market data, calculating indicators, and running trading strategies in a deterministic, backtest-ready environment.

## 1. Feature Engineering (`app/quantitative/features`)
The `features/core.py` module exposes pure, stateless functions to calculate technical indicators such as SMA, EMA, RSI, ATR, Volatility, and Returns.
- **Constraints**: No look-ahead bias is permitted. Pandas `.rolling()` is used with correct `min_periods` behavior.
- **Independence**: Features calculate across a `pd.DataFrame` entirely independent of the database or ingestion engine.

## 2. BaseStrategy Interface (`app/strategies/base.py`)
All strategies inherit from `BaseStrategy`.
- Defines static properties: `id`, `name`, `version`, `description`, `required_features`.
- Abstract method `generate_signals(df: pd.DataFrame) -> List[StrategySignal]` takes pre-processed market data (augmented with required features) and generates deterministic, structured signals.

### StrategySignal Model
Standardized plain data structure emitted by strategies.
- `symbol`
- `timestamp`
- `direction` (1: Long, -1: Short, 0: Flat)
- `strategy_id`
- `strategy_version`
- `confidence`, `reason`, `metadata`

## 3. Strategy Registry (`app/strategies/registry.py`)
A plugin-style architecture where strategies are decorated with `@register_strategy`.
- Handles instantiation with parameters via `StrategyRegistry.get_strategy(id, **params)`.
- Prevents direct hardcoding of strategy imports in higher-level execution components.

## 4. Concrete Strategies
1. **MomentumStrategy** (`app/strategies/momentum/strategy.py`):
   - Uses `SMA` and `RSI`.
   - Entry Long: Price > SMA and RSI > Threshold.
2. **MeanReversionStrategy** (`app/strategies/mean_reversion/strategy.py`):
   - Uses `RSI`.
   - Entry Long: RSI < Oversold Threshold.

## Strict Architectural Enforcement
- **No Persistence**: Strategies do not perform database operations.
- **No Execution**: Strategies only return standard signals; they do not interact with brokers or paper trading.
- **Determinism**: Tests explicitly ensure strategies are deterministic and devoid of future-data leaks.
