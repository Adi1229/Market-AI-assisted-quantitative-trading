from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import uuid
import asyncio

from app.backtesting.engine import BacktestEngine
from app.backtesting.models import BacktestConfig
from app.api.schemas import BacktestRequest, BacktestResponse

router = APIRouter()

# In-memory store for MVP backtests
_backtests_store = {}

@router.post("/backtests", response_model=BacktestResponse)
async def run_backtest(req: BacktestRequest):
    """Run a backtest using the requested strategy."""
    try:
        # Pass dummy df since we don't have db wired to data provider in MVP UI yet
        import pandas as pd
        import numpy as np
        
        # Create dummy df spanning requested dates
        dates = pd.date_range(req.start_date, req.end_date, freq='D')
        df = pd.DataFrame({
            "open": np.random.normal(100, 2, len(dates)),
            "high": np.random.normal(105, 2, len(dates)),
            "low": np.random.normal(95, 2, len(dates)),
            "close": np.random.normal(102, 2, len(dates)),
            "volume": np.random.randint(1000, 5000, len(dates))
        }, index=dates)
        
        config = BacktestConfig(
            strategy_id=req.strategy_id,
            symbol=req.symbol,
            initial_capital=req.initial_capital
        )
        engine = BacktestEngine(config=config)
        
        result = engine.run(df=df)
        
        bt_id = str(uuid.uuid4())
        _backtests_store[bt_id] = result
        
        return BacktestResponse(
            backtest_id=bt_id,
            strategy_id=req.strategy_id,
            symbol=req.symbol,
            total_return=result.metrics.total_return,
            cagr=result.metrics.cagr,
            sharpe_ratio=result.metrics.sharpe_ratio,
            max_drawdown=result.metrics.max_drawdown,
            win_rate=result.metrics.win_rate,
            total_trades=result.metrics.total_trades,
            profit_factor=result.metrics.profit_factor
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtests/{backtest_id}", response_model=BacktestResponse)
def get_backtest_result(backtest_id: str):
    """Get full backtest result and metrics."""
    result = _backtests_store.get(backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest not found.")
        
    return BacktestResponse(
        backtest_id=backtest_id,
        strategy_id="momentum_v1", # Mocked
        symbol="RELIANCE",
        total_return=result.total_return,
        cagr=result.cagr,
        sharpe_ratio=result.sharpe_ratio,
        max_drawdown=result.max_drawdown,
        win_rate=result.win_rate,
        total_trades=result.total_trades,
        profit_factor=result.profit_factor
    )

@router.get("/backtests/{backtest_id}/trades")
def get_backtest_trades(backtest_id: str):
    """Get individual trades from backtest."""
    result = _backtests_store.get(backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest not found.")
        
    return {"trades": [t.dict() for t in result.trades]}
