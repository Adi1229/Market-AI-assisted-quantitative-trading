import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta
from app.strategies.momentum.strategy import MomentumStrategy

def test_strategy_signal_timestamp():
    """Test that a signal timestamp corresponds exactly to the completed candle."""
    strategy = MomentumStrategy(sma_window=2, rsi_window=2, rsi_long_threshold=50, rsi_short_threshold=50)
    
    # Create 5 candles
    base_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    data = []
    for i in range(5):
        # Trending up, RSI will be high, Close > SMA
        close_price = 100 + (i * 10)
        sma = 100 + (i * 5)
        rsi = 60 + i
        data.append({
            "timestamp": base_time + timedelta(minutes=5*i),
            "close": close_price,
            "SMA_2": sma,
            "RSI_2": rsi
        })
    df = pd.DataFrame(data)
    
    signals = strategy.generate_signals(df)
    
    assert len(signals) > 0
    # Check that each signal corresponds to a row timestamp
    df_timestamps = [pd.Timestamp(ts) for ts in df['timestamp']]
    for signal in signals:
        assert pd.Timestamp(signal.timestamp) in df_timestamps
        assert signal.direction == 1 # All should be BUY

def test_strategy_ignores_flat_candles():
    """Test that if the latest candle is flat, no signal is fabricated for it."""
    strategy = MomentumStrategy(sma_window=2, rsi_window=2, rsi_long_threshold=50, rsi_short_threshold=50)
    
    base_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    data = []
    for i in range(4):
        # Trending up
        data.append({
            "timestamp": base_time + timedelta(minutes=5*i),
            "close": 100 + (i * 10),
            "SMA_2": 100 + (i * 5),
            "RSI_2": 60 + i
        })
    # Last candle is FLAT
    data.append({
        "timestamp": base_time + timedelta(minutes=20),
        "close": 100, # below SMA
        "SMA_2": 150,
        "RSI_2": 60   # above 50, conflicting conditions -> FLAT
    })
    
    df = pd.DataFrame(data)
    signals = strategy.generate_signals(df)
    
    assert len(signals) > 0
    latest_signal = signals[-1]
    
    # Latest signal should NOT be the last candle
    assert latest_signal.timestamp != data[-1]["timestamp"]
    assert latest_signal.timestamp == data[-2]["timestamp"]

def test_no_future_data():
    """Test that strategy evaluates sequentially without lookahead."""
    strategy = MomentumStrategy(sma_window=2, rsi_window=2, rsi_long_threshold=50, rsi_short_threshold=50)
    base_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    
    df1 = pd.DataFrame([{
        "timestamp": base_time,
        "close": 110, "SMA_2": 100, "RSI_2": 60
    }])
    
    df2 = pd.DataFrame([{
        "timestamp": base_time,
        "close": 110, "SMA_2": 100, "RSI_2": 60
    }, {
        "timestamp": base_time + timedelta(minutes=5),
        "close": 120, "SMA_2": 105, "RSI_2": 70
    }])
    
    signals1 = strategy.generate_signals(df1)
    signals2 = strategy.generate_signals(df2)
    
    assert len(signals1) == 1
    assert len(signals2) == 2
    # The first signal should be exactly identical
    assert signals1[0].timestamp == signals2[0].timestamp
    assert signals1[0].direction == signals2[0].direction
