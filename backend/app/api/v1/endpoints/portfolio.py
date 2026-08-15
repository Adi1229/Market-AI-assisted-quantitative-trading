from fastapi import APIRouter, Depends
from typing import List

from app.api.dependencies import get_execution_provider, get_portfolio
from app.engine.execution import PaperExecutionProvider
from app.engine.portfolio import VirtualPortfolio
from app.api.schemas import (
    PortfolioSummaryResponse, PositionResponse, OrderResponse, 
    MessageResponse, ExecutionModeUpdate
)

router = APIRouter()

@router.get("/portfolio/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(provider: PaperExecutionProvider = Depends(get_execution_provider)):
    """Get virtual portfolio summary and P&L."""
    # Dummy current prices for MVP
    current_prices = {"RELIANCE": 2450.0, "INFY": 1400.0, "HDFC": 1500.0, "TCS": 3500.0}
    summary = await provider.get_portfolio_summary(current_prices)
    
    return PortfolioSummaryResponse(
        total_value=summary.total_value,
        cash=summary.cash,
        positions_value=summary.positions_value,
        unrealized_pnl=summary.unrealized_pnl,
        realized_pnl=summary.realized_pnl,
        total_pnl=summary.total_pnl,
        exposure_pct=summary.exposure_pct,
        drawdown=summary.drawdown,
        max_drawdown=summary.max_drawdown,
        open_positions=summary.open_positions,
        total_trades=summary.total_trades
    )

@router.get("/portfolio/positions", response_model=List[PositionResponse])
async def get_positions(provider: PaperExecutionProvider = Depends(get_execution_provider)):
    """Get open positions."""
    positions = await provider.get_positions()
    return [
        PositionResponse(
            instrument_id=p.instrument_id,
            direction=p.direction,
            quantity=p.quantity,
            entry_price=p.entry_price,
            current_price=p.current_price,
            unrealized_pnl=p.unrealized_pnl,
            opened_at=p.opened_at
        ) for p in positions
    ]

@router.get("/portfolio/orders", response_model=List[OrderResponse])
def get_orders(portfolio: VirtualPortfolio = Depends(get_portfolio)):
    """Get recent orders."""
    return [
        OrderResponse(
            order_id=o.order_id,
            opportunity_id=o.opportunity_id,
            instrument_id=o.instrument_id,
            direction=o.direction,
            order_type=o.order_type,
            quantity=o.quantity,
            status=o.status.value,
            fill_price=o.fill_price,
            commission=o.commission,
            slippage=o.slippage,
            created_at=o.created_at,
            filled_at=o.filled_at
        ) for o in portfolio.orders
    ]

@router.put("/execution/mode", response_model=MessageResponse)
def set_execution_mode(req: ExecutionModeUpdate):
    """Configure execution mode (PAPER, LIVE)."""
    if req.mode == "LIVE":
        # Cannot be set to LIVE without actual implementation
        return MessageResponse(message="LIVE execution is currently disabled for MVP safety.")
    return MessageResponse(message=f"Execution mode set to {req.mode}")

@router.get("/execution/status")
def get_execution_status(provider: PaperExecutionProvider = Depends(get_execution_provider)):
    """Get execution engine health and active mode."""
    return {
        "status": "Healthy",
        "provider": provider.provider_id,
        "mode": provider.execution_mode
    }
