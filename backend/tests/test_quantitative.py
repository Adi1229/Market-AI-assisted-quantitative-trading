import pytest
import pandas as pd
import numpy as np
from app.quantitative.features.core import (
    calculate_returns,
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_atr,
    calculate_volatility
)

@pytest.fixture
def sample_df():
    # Deterministic price data
    dates = pd.date_range("2023-01-01", periods=20, freq="D")
    df = pd.DataFrame({
        "open": np.linspace(100, 120, 20),
        "high": np.linspace(105, 125, 20),
        "low": np.linspace(95, 115, 20),
        "close": np.linspace(102, 122, 20),
        "volume": np.ones(20) * 1000
    }, index=dates)
    return df

def test_calculate_returns(sample_df):
    returns = calculate_returns(sample_df)
    assert len(returns) == 20
    assert pd.isna(returns.iloc[0]) # First row is NaN
    assert not pd.isna(returns.iloc[-1])

def test_calculate_sma(sample_df):
    sma = calculate_sma(sample_df, window=5)
    assert pd.isna(sma.iloc[3])
    assert not pd.isna(sma.iloc[4])
    assert np.isclose(sma.iloc[4], sample_df["close"].iloc[0:5].mean())

def test_calculate_ema(sample_df):
    ema = calculate_ema(sample_df, window=5)
    assert pd.isna(ema.iloc[3])
    assert not pd.isna(ema.iloc[4])

def test_calculate_rsi(sample_df):
    # For a monotonically increasing series, RSI should be 100
    rsi = calculate_rsi(sample_df, window=14)
    assert pd.isna(rsi.iloc[13])
    assert not pd.isna(rsi.iloc[14])
    assert rsi.iloc[-1] == 100.0

def test_calculate_atr(sample_df):
    atr = calculate_atr(sample_df, window=14)
    assert pd.isna(atr.iloc[12])
    assert not pd.isna(atr.iloc[-1])

def test_calculate_volatility(sample_df):
    vol = calculate_volatility(sample_df, window=5)
    assert pd.isna(vol.iloc[4]) # window 5 of returns (which has NaN at 0) means it needs 6 rows
    assert not pd.isna(vol.iloc[-1])

def test_no_lookahead_bias(sample_df):
    # Modify the last value
    df_modified = sample_df.copy()
    df_modified.loc[df_modified.index[-1], "close"] = 9999
    
    sma_original = calculate_sma(sample_df, window=5)
    sma_modified = calculate_sma(df_modified, window=5)
    
    # The SMA at index -2 should be exactly the same
    assert sma_original.iloc[-2] == sma_modified.iloc[-2]
    # The SMA at index -1 should be different
    assert sma_original.iloc[-1] != sma_modified.iloc[-1]
