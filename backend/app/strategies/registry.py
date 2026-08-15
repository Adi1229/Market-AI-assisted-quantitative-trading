from typing import Dict, Type, List
from app.strategies.base import BaseStrategy

class StrategyRegistry:
    """
    Registry for managing and instantiating strategies.
    Supports a plugin-style architecture where strategies can be registered 
    and dynamically loaded by ID.
    """
    
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    @classmethod
    def register(cls, strategy_class: Type[BaseStrategy]):
        """
        Register a strategy class with the registry.
        Instantiates a temporary instance to extract the static ID.
        """
        # Create a dummy instance just to read the properties if they aren't class methods
        # However, to allow parameterized strategies, we require the strategy class
        # to have a hardcoded ID property that doesn't depend on parameters.
        # Let's instantiate it with no args to get the ID.
        try:
            temp_instance = strategy_class()
            strategy_id = temp_instance.id
            cls._strategies[strategy_id] = strategy_class
        except Exception as e:
            raise ValueError(f"Failed to register strategy {strategy_class.__name__}: {str(e)}")
            
        return strategy_class
        
    @classmethod
    def get_strategy(cls, strategy_id: str, **parameters) -> BaseStrategy:
        """
        Retrieve and instantiate a strategy by its ID with the given parameters.
        """
        if strategy_id not in cls._strategies:
            raise KeyError(f"Strategy with ID '{strategy_id}' not found in registry.")
            
        strategy_class = cls._strategies[strategy_id]
        return strategy_class(**parameters)
        
    @classmethod
    def list_strategies(cls) -> List[Dict[str, str]]:
        """
        List all available strategies with their basic metadata.
        """
        strategies_info = []
        for strategy_id, strategy_class in cls._strategies.items():
            temp = strategy_class()
            strategies_info.append({
                "id": temp.id,
                "name": temp.name,
                "version": temp.version,
                "description": temp.description,
            })
        return strategies_info

def register_strategy(strategy_class: Type[BaseStrategy]):
    """Decorator for registering a strategy."""
    return StrategyRegistry.register(strategy_class)
