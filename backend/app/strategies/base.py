from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import pandas as pd

class StrategySignal(BaseModel):
    """
    Standardized signal produced by any strategy in the Quantitative Engine.
    Direction: 1 (Long), -1 (Short), 0 (Flat/Close)
    """
    symbol: str = Field(..., description="Instrument symbol")
    timestamp: datetime = Field(..., description="Time of the signal")
    direction: int = Field(..., description="1 for Long, -1 for Short, 0 for Flat")
    strategy_id: str = Field(..., description="ID of the strategy generating the signal")
    strategy_version: str = Field(..., description="Version of the strategy")
    confidence: Optional[float] = Field(None, description="Confidence score [0.0, 1.0]")
    reason: Optional[str] = Field(None, description="Human-readable reason for the signal")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or feature values")

class BaseStrategy(ABC):
    """
    Standardized Strategy Interface.
    All strategies must inherit from this class and implement generate_signals.
    """
    
    def __init__(self, **parameters):
        self.parameters = parameters
        self.validate_parameters()
        
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the strategy."""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the strategy."""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the strategy (e.g., '1.0.0')."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of the strategy's logic and behavior."""
        pass
        
    @property
    @abstractmethod
    def required_features(self) -> List[str]:
        """
        List of feature names required by this strategy. 
        These must be pre-computed and present as columns in the DataFrame 
        passed to generate_signals.
        """
        pass

    def validate_parameters(self) -> None:
        """
        Validate the parameters passed during initialization.
        Override to implement custom validation logic.
        Raise ValueError for invalid configuration.
        """
        pass

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[StrategySignal]:
        """
        Core signal generation logic.
        Takes a DataFrame containing market data and pre-computed features.
        Returns a list of StrategySignal objects.
        """
        pass
