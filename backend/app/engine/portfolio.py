from typing import List, Optional
from datetime import datetime
from app.engine.models import ExecutionPosition, ExecutionOrder, PortfolioSummary

class VirtualPortfolio:
    """
    Deterministically manages the paper trading portfolio.
    """
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: List[ExecutionPosition] = []
        self.orders: List[ExecutionOrder] = []
        self.realized_pnl = 0.0
        
    def add_order(self, order: ExecutionOrder):
        self.orders.append(order)
        
    def get_positions(self) -> List[ExecutionPosition]:
        return self.positions
        
    def get_open_orders(self) -> List[ExecutionOrder]:
        return [o for o in self.orders if o.status == "pending"]
        
    def update_position(self, order: ExecutionOrder, current_time: datetime):
        """
        Applies a filled order to the portfolio positions and cash.
        """
        cost_basis = order.fill_price * order.quantity
        commission = order.commission or 0.0
        
        # Deduct cash for buys, add for sells (simplistic, assumes cash account, no margin)
        if order.direction == "BUY":
            self.cash -= (cost_basis + commission)
            
            # Find existing position
            existing = next((p for p in self.positions if p.instrument_id == order.instrument_id and p.direction == "LONG"), None)
            if existing:
                # Average up/down
                total_qty = existing.quantity + order.quantity
                avg_price = ((existing.entry_price * existing.quantity) + cost_basis) / total_qty
                existing.quantity = total_qty
                existing.entry_price = avg_price
            else:
                self.positions.append(ExecutionPosition(
                    instrument_id=order.instrument_id,
                    direction="LONG",
                    quantity=order.quantity,
                    entry_price=order.fill_price,
                    current_price=order.fill_price,
                    unrealized_pnl=0.0,
                    opened_at=current_time
                ))
                
        elif order.direction == "SELL":
            self.cash += (cost_basis - commission)
            
            # Find existing long to close
            existing = next((p for p in self.positions if p.instrument_id == order.instrument_id and p.direction == "LONG"), None)
            if existing:
                # Close out or partial
                if order.quantity >= existing.quantity:
                    # Full close
                    pnl = (order.fill_price - existing.entry_price) * existing.quantity
                    self.realized_pnl += pnl - commission
                    self.positions.remove(existing)
                else:
                    # Partial close
                    pnl = (order.fill_price - existing.entry_price) * order.quantity
                    self.realized_pnl += pnl - commission
                    existing.quantity -= order.quantity
            else:
                # Short selling (simplistic)
                self.positions.append(ExecutionPosition(
                    instrument_id=order.instrument_id,
                    direction="SHORT",
                    quantity=order.quantity,
                    entry_price=order.fill_price,
                    current_price=order.fill_price,
                    unrealized_pnl=0.0,
                    opened_at=current_time
                ))

    def get_summary(self, current_prices: dict) -> PortfolioSummary:
        """
        Generates current portfolio summary based on latest prices.
        """
        positions_value = 0.0
        unrealized_pnl = 0.0
        
        for pos in self.positions:
            current_price = current_prices.get(pos.instrument_id, pos.current_price)
            pos.current_price = current_price
            if pos.direction == "LONG":
                pos.unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
                positions_value += current_price * pos.quantity
            else:
                pos.unrealized_pnl = (pos.entry_price - current_price) * pos.quantity
                # Simplifying short value
                positions_value += pos.entry_price * pos.quantity 
            unrealized_pnl += pos.unrealized_pnl
            
        total_value = self.cash + positions_value + unrealized_pnl
        total_pnl = self.realized_pnl + unrealized_pnl
        exposure = (positions_value / total_value) * 100 if total_value > 0 else 0.0
        
        return PortfolioSummary(
            total_value=total_value,
            cash=self.cash,
            positions_value=positions_value,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=self.realized_pnl,
            total_pnl=total_pnl,
            exposure_pct=exposure,
            drawdown=0.0, # Not calculating complex drawdown in MVP memory state
            max_drawdown=0.0,
            open_positions=len(self.positions),
            total_trades=len([o for o in self.orders if o.status == "filled"])
        )
