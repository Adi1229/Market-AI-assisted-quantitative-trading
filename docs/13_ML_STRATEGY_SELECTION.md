# 13 — ML Strategy Selection Design

| Field | Value |
|---|---|
| **Document ID** | MLS-001 |
| **Version** | 0.2.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Signal Engine](./36_SIGNAL_ENGINE.md), [Strategy Framework](./10_STRATEGY_FRAMEWORK.md), [Backtesting Engine](./11_BACKTESTING_ENGINE.md) |

---

## 1. Purpose

The ML component acts as a **strategy-ranking/selection layer**. It predicts which strategies from the Strategy Studio are most likely to perform well under current market conditions. 

It is *not* an autonomous trading decision-maker; its outputs are consumed by users or by the Signal Engine to inform Strategy-Only or Hybrid decision modes.

---

## 2. Problem Definition

**Given** a snapshot of current market conditions (features) and a portfolio of registered strategies, **predict** the ranking of those strategies for near-term forward performance.

---

## 3. Model Selection

| Phase | Model | Justification |
|---|---|---|
| **Baseline** | Logistic Regression | Simplest; interpretable; sanity check |
| **Primary (MVP)**| LightGBM / XGBoost | State-of-the-art for tabular data; fast; feature importance |
| **Comparison** | Random Forest | Non-linear; stable |
| **Future** | Neural Network | Only if data volume/complexity strongly justify it |

> [!NOTE]
> Deep learning models are documented as a future option only, per client preference to evaluate simpler models first.

---

## 4. Training Dataset & Features

### 4.1 Target Variable
* **Initial MVP:** Binary classification (Strategy outperforms a defined threshold/benchmark).
* **Evolution:** Learning to Rank (directly predicting relative rank of strategies).

### 4.2 Feature Set (Market Conditions)
* Trend strength (ADX)
* Volatility regime (Historical Vol, ATR)
* Market breadth (Advancing vs Declining)
* Momentum regime
* Correlation regime

### 4.3 Feature Set (Strategy Historical Performance)
* Recent rolling Sharpe ratio
* Recent win rate
* Recent max drawdown

---

## 5. Time-Series Validation (CLIENT-CONFIRMED)

Random train/test splitting must **never** be used.

* **Walk-forward CV:** Train on `[0, T]`, validate on `[T, T+V]`, advance and repeat.
* **Purged CV:** Insert a temporal gap between training and validation sets to prevent data leakage (e.g., predicting forward returns requires purging the forward window).

---

## 6. Integration with Signal Engine

The ML Strategy Selection model produces a `StrategyRanking` object. 

In the platform workflow:
1. The user views the ML Strategy Rankings in the dashboard.
2. The user activates the top-ranked strategy in the Strategy Studio.
3. The Signal Engine uses that activated strategy for generating opportunities in `STRATEGY_ONLY` or `HYBRID` modes.

*(The ML Ranking layer does not independently generate trade signals; it manages strategy selection.)*

---

## 7. Model Versioning & Drift

* **Metadata Tracking:** Every trained model records its version, hyperparameters, features used, and validation metrics.
* **Drift Monitoring (Phase 2):** Monitor for feature distribution shift and ranking stability degradation over time.

---

## 8. Cross-References

| Document | Relevance |
|---|---|
| [Signal Engine](./36_SIGNAL_ENGINE.md) | Consumes strategies ranked by this ML layer |
| [Backtesting Engine](./11_BACKTESTING_ENGINE.md) | Generates the training target data (historical performance) |
| [MLOps & Reproducibility](./21_MLOPS_AND_REPRODUCIBILITY.md) | Tracking model versions |
