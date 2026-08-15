import pandas as pd
from app.intelligence.models import MarketRegime
import app.quantitative.features.core as features

class MarketRegimeAnalyzer:
    """
    Deterministically classifies the market regime at a specific timestamp based on quantitative features.
    """
    
    @staticmethod
    def classify(df: pd.DataFrame, symbol: str, timestamp: pd.Timestamp) -> MarketRegime:
        """
        Calculates regime at the specific timestamp.
        Assumes df contains data up to the timestamp (no look-ahead).
        """
        # We need historical data to compute SMA/Volatility
        # In a real environment, we'd pre-compute this or fetch pre-computed features.
        # For simplicity, we compute on the fly here using a slice up to the timestamp.
        
        df_slice = df.loc[:timestamp].copy()
        if len(df_slice) < 50:
            # Not enough data for 50-period SMA
            return MarketRegime(
                symbol=symbol,
                timestamp=timestamp,
                trend_state="Neutral",
                volatility_state="Neutral",
                momentum_state="Neutral",
                features_used={}
            )
            
        # Compute features
        close = df_slice["close"].iloc[-1]
        sma_20 = features.calculate_sma(df_slice, window=20).iloc[-1]
        sma_50 = features.calculate_sma(df_slice, window=50).iloc[-1]
        rsi_14 = features.calculate_rsi(df_slice, window=14).iloc[-1]
        volatility_20 = features.calculate_volatility(df_slice, window=20).iloc[-1]
        
        # Trend
        if close > sma_20 > sma_50:
            trend_state = "Bullish"
        elif close < sma_20 < sma_50:
            trend_state = "Bearish"
        else:
            trend_state = "Neutral"
            
        # Volatility (Simple threshold for demonstration)
        # Assuming daily returns, a standard deviation > 0.02 (2%) is high volatility
        volatility_state = "High" if volatility_20 > 0.02 else "Low"
        
        # Momentum
        if rsi_14 > 70:
            momentum_state = "Overbought"
        elif rsi_14 < 30:
            momentum_state = "Oversold"
        else:
            momentum_state = "Neutral"
            
        features_used = {
            "close": float(close),
            "SMA_20": float(sma_20),
            "SMA_50": float(sma_50),
            "RSI_14": float(rsi_14),
            "VOLATILITY_20": float(volatility_20)
        }
        
        return MarketRegime(
            symbol=symbol,
            timestamp=timestamp,
            trend_state=trend_state,
            volatility_state=volatility_state,
            momentum_state=momentum_state,
            features_used=features_used
        )
