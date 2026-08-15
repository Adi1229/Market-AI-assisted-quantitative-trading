from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.api.dependencies import get_strategy_registry
from app.strategies.registry import StrategyRegistry
from app.api.schemas import StrategyResponse, MessageResponse

router = APIRouter()

@router.get("/strategies", response_model=List[StrategyResponse])
def list_strategies(registry: type[StrategyRegistry] = Depends(get_strategy_registry)):
    """List all registered strategies."""
    results = []
    strats = registry.list_strategies()
    for s_info in strats:
        results.append(
            StrategyResponse(
                id=s_info["id"],
                name=s_info["name"],
                version=s_info["version"],
                description=s_info["description"],
                status="ACTIVE"
            )
        )
    return results

@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: str, registry: type[StrategyRegistry] = Depends(get_strategy_registry)):
    """Get single strategy metadata."""
    try:
        strat = registry.get_strategy(strategy_id)
        return StrategyResponse(
            id=strat.id,
            name=strat.name,
            version=strat.version,
            description=strat.description,
            status="ACTIVE"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found.")

@router.post("/strategies/{strategy_id}/activate", response_model=MessageResponse)
def activate_strategy(strategy_id: str, registry: type[StrategyRegistry] = Depends(get_strategy_registry)):
    try:
        registry.get_strategy(strategy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found.")
    # In MVP, activation is just mocked at the registry level
    return MessageResponse(message=f"Strategy {strategy_id} set to ACTIVE")

@router.post("/strategies/{strategy_id}/deactivate", response_model=MessageResponse)
def deactivate_strategy(strategy_id: str, registry: type[StrategyRegistry] = Depends(get_strategy_registry)):
    try:
        registry.get_strategy(strategy_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found.")
    return MessageResponse(message=f"Strategy {strategy_id} set to INACTIVE")
