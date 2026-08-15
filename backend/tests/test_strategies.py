import pytest
import pandas as pd
from app.strategies.registry import StrategyRegistry
from app.strategies.momentum.strategy import MomentumStrategy
from app.strategies.mean_reversion.strategy import MeanReversionStrategy
from app.strategies.base import BaseStrategy

def test_registry_has_strategies():
    strategies = StrategyRegistry.list_strategies()
    assert len(strategies) >= 2
    ids = [s["id"] for s in strategies]
    assert "momentum_v1" in ids
    assert "mean_reversion_rsi_v1" in ids

def test_get_strategy_from_registry():
    strategy = StrategyRegistry.get_strategy("momentum_v1", sma_window=10)
    assert isinstance(strategy, MomentumStrategy)
    assert strategy.parameters["sma_window"] == 10

def test_invalid_strategy_id():
    with pytest.raises(KeyError):
        StrategyRegistry.get_strategy("non_existent_strategy")

def test_momentum_strategy_signals():
    strategy = MomentumStrategy(sma_window=3, rsi_window=3, rsi_long_threshold=60, rsi_short_threshold=40)
    
    # Create a dummy DataFrame with the required features already computed
    df = pd.DataFrame({
        "symbol": ["AAPL", "AAPL", "AAPL"],
        "close": [100, 110, 90],
        "SMA_3": [95, 105, 95], # close > SMA for first two, close < SMA for last
        "RSI_3": [65, 75, 30]   # RSI > 60 for first two, RSI < 40 for last
    }, index=pd.date_range("2023-01-01", periods=3))
    
    signals = strategy.generate_signals(df)
    
    assert len(signals) == 3
    assert signals[0].direction == 1
    assert signals[1].direction == 1
    assert signals[2].direction == -1

def test_mean_reversion_strategy_signals():
    strategy = MeanReversionStrategy(rsi_window=14, oversold_threshold=30, overbought_threshold=70)
    
    df = pd.DataFrame({
        "symbol": ["TSLA", "TSLA", "TSLA"],
        "RSI_14": [20, 50, 80]
    }, index=pd.date_range("2023-01-01", periods=3))
    
    signals = strategy.generate_signals(df)
    
    assert len(signals) == 2
    assert signals[0].direction == 1  # Oversold (<30)
    assert signals[1].direction == -1 # Overbought (>70)

def test_missing_features():
    strategy = MomentumStrategy()
    df = pd.DataFrame({"close": [100]})
    with pytest.raises(ValueError, match="Missing required features"):
        strategy.generate_signals(df)

def test_nan_handling():
    strategy = MeanReversionStrategy(rsi_window=14)
    # Provide NaN, which happens during indicator warmup
    df = pd.DataFrame({
        "symbol": ["MSFT"],
        "RSI_14": [float("nan")]
    }, index=[pd.Timestamp("2023-01-01")])
    
    signals = strategy.generate_signals(df)
    assert len(signals) == 0

def test_parameter_validation():
    with pytest.raises(ValueError):
        MeanReversionStrategy(oversold_threshold=80, overbought_threshold=20)
