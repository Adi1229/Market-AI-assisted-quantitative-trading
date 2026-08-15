import pandas as pd
from typing import List
from app.strategies.base import BaseStrategy, StrategySignal
from app.strategies.registry import register_strategy

@register_strategy
class MomentumStrategy(BaseStrategy):
    """
    A simple Momentum Strategy.
    Generates a Long signal when the price closes above the SMA and RSI is above a threshold.
    Generates a Short signal when the price closes below the SMA and RSI is below a threshold.
    """
    
    def __init__(self, sma_window: int = 50, rsi_window: int = 14, 
                 rsi_long_threshold: float = 50.0, rsi_short_threshold: float = 50.0):
        super().__init__(
            sma_window=sma_window, 
            rsi_window=rsi_window,
            rsi_long_threshold=rsi_long_threshold,
            rsi_short_threshold=rsi_short_threshold
        )
        
    @property
    def id(self) -> str:
        return "momentum_v1"
        
    @property
    def name(self) -> str:
        return "Momentum Strategy"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Simple momentum strategy based on SMA crossover and RSI filtering."
        
    @property
    def required_features(self) -> List[str]:
        # The engine will need to know which features to compute.
        # We can dynamically name them based on parameters, but for simplicity
        # we'll expect features named 'SMA' and 'RSI' in the DataFrame.
        # Or, more deterministically:
        return [f"SMA_{self.parameters['sma_window']}", f"RSI_{self.parameters['rsi_window']}"]
        
    def validate_parameters(self) -> None:
        if self.parameters.get("sma_window", 0) <= 0:
            raise ValueError("sma_window must be > 0")
        if self.parameters.get("rsi_window", 0) <= 0:
            raise ValueError("rsi_window must be > 0")

    def generate_signals(self, df: pd.DataFrame) -> List[StrategySignal]:
        signals = []
        
        sma_col = f"SMA_{self.parameters['sma_window']}"
        rsi_col = f"RSI_{self.parameters['rsi_window']}"
        
        if sma_col not in df.columns or rsi_col not in df.columns:
            raise ValueError(f"Missing required features: {sma_col}, {rsi_col}")
            
        rsi_long = self.parameters["rsi_long_threshold"]
        rsi_short = self.parameters["rsi_short_threshold"]
        
        for idx, row in df.iterrows():
            # Skip if we don't have enough data (NaN features)
            if pd.isna(row[sma_col]) or pd.isna(row[rsi_col]):
                continue
                
            direction = 0
            reason = ""
            
            # Entry logic
            if row["close"] > row[sma_col] and row[rsi_col] > rsi_long:
                direction = 1
                reason = "Close > SMA and RSI > Threshold"
            elif row["close"] < row[sma_col] and row[rsi_col] < rsi_short:
                direction = -1
                reason = "Close < SMA and RSI < Threshold"
                
            if direction != 0:
                signal = StrategySignal(
                    symbol=row.get("symbol", "UNKNOWN"), # Typically part of the df or passed separately
                    timestamp=idx if isinstance(idx, pd.Timestamp) else row.get("timestamp"),
                    direction=direction,
                    strategy_id=self.id,
                    strategy_version=self.version,
                    reason=reason,
                    metadata={
                        "close": float(row["close"]),
                        "sma": float(row[sma_col]),
                        "rsi": float(row[rsi_col])
                    }
                )
                signals.append(signal)
                
        return signals
