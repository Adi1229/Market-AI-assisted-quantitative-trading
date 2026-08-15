import pandas as pd
from typing import List
from app.strategies.base import BaseStrategy, StrategySignal
from app.strategies.registry import register_strategy

@register_strategy
class MeanReversionStrategy(BaseStrategy):
    """
    A Mean Reversion Strategy based on RSI.
    Generates a Long signal when RSI drops below the oversold threshold.
    Generates a Short signal when RSI rises above the overbought threshold.
    """
    
    def __init__(self, rsi_window: int = 14, 
                 oversold_threshold: float = 30.0, overbought_threshold: float = 70.0):
        super().__init__(
            rsi_window=rsi_window,
            oversold_threshold=oversold_threshold,
            overbought_threshold=overbought_threshold
        )
        
    @property
    def id(self) -> str:
        return "mean_reversion_rsi_v1"
        
    @property
    def name(self) -> str:
        return "Mean Reversion Strategy (RSI)"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Counter-trend strategy using RSI to identify overbought/oversold conditions."
        
    @property
    def required_features(self) -> List[str]:
        return [f"RSI_{self.parameters['rsi_window']}"]
        
    def validate_parameters(self) -> None:
        if self.parameters.get("rsi_window", 0) <= 0:
            raise ValueError("rsi_window must be > 0")
        if self.parameters.get("oversold_threshold", 0) >= self.parameters.get("overbought_threshold", 0):
            raise ValueError("oversold_threshold must be strictly less than overbought_threshold")

    def generate_signals(self, df: pd.DataFrame) -> List[StrategySignal]:
        signals = []
        
        rsi_col = f"RSI_{self.parameters['rsi_window']}"
        
        if rsi_col not in df.columns:
            raise ValueError(f"Missing required feature: {rsi_col}")
            
        oversold = self.parameters["oversold_threshold"]
        overbought = self.parameters["overbought_threshold"]
        
        for idx, row in df.iterrows():
            if pd.isna(row[rsi_col]):
                continue
                
            direction = 0
            reason = ""
            
            # Entry logic
            if row[rsi_col] < oversold:
                direction = 1
                reason = "RSI Oversold"
            elif row[rsi_col] > overbought:
                direction = -1
                reason = "RSI Overbought"
                
            if direction != 0:
                signal = StrategySignal(
                    symbol=row.get("symbol", "UNKNOWN"),
                    timestamp=idx if isinstance(idx, pd.Timestamp) else row.get("timestamp"),
                    direction=direction,
                    strategy_id=self.id,
                    strategy_version=self.version,
                    reason=reason,
                    metadata={
                        "rsi": float(row[rsi_col])
                    }
                )
                signals.append(signal)
                
        return signals
