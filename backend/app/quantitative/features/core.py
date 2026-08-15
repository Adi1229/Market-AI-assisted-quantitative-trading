import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame, column: str = "close") -> pd.Series:
    """Calculate simple percentage returns."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return df[column].pct_change()

def calculate_sma(df: pd.DataFrame, window: int, column: str = "close") -> pd.Series:
    """Calculate Simple Moving Average."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return df[column].rolling(window=window, min_periods=window).mean()

def calculate_ema(df: pd.DataFrame, window: int, column: str = "close") -> pd.Series:
    """Calculate Exponential Moving Average."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    return df[column].ewm(span=window, adjust=False, min_periods=window).mean()

def calculate_rsi(df: pd.DataFrame, window: int = 14, column: str = "close") -> pd.Series:
    """Calculate Relative Strength Index."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")
    delta = df[column].diff()
    gain = delta.clip(lower=0).rolling(window=window, min_periods=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window, min_periods=window).mean()
    rs = gain / loss
    
    rsi = 100 - (100 / (1 + rs))
    # Replace division by zero cases. If loss is 0, RSI is 100.
    rsi = rsi.mask(loss == 0, 100)
    return rsi

def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    required = ["high", "low", "close"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
            
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=window, min_periods=window).mean()

def calculate_volatility(df: pd.DataFrame, window: int, column: str = "close") -> pd.Series:
    """Calculate rolling volatility (standard deviation of returns)."""
    returns = calculate_returns(df, column=column)
    return returns.rolling(window=window, min_periods=window).std()
