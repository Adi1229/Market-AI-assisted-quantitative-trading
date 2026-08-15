import uuid
from typing import Dict, List, Optional
from datetime import datetime
from app.backtesting.models import Order, Trade, Position

class Portfolio:
    """
    Manages cash, open positions, and processes fills.
    """
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        # Key: symbol, Value: Position
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        
    def process_fill(self, order: Order, fill_price: float, fee: float, fill_timestamp: datetime, strategy_id: str):
        print(f"Processing fill: {order.side} qty={order.quantity} at {fill_price}")
        self.cash -= fee
        
        pos = self.positions.get(order.symbol)
        print(f"Current position: {pos}")
        
        # We only support simple Long positions for now. Flat/Close orders close the position.
        # Shorting would require margin accounting, which we avoid in this simple Phase 3 model
        # unless explicitly requested. But we can handle closing a Long position easily.
        
        if order.side == 1:
            # Buy order
            cost = order.quantity * fill_price
            if cost > self.cash:
                # We can only buy what we can afford. 
                # For simplicity, if we request an impossible amount, we reject or scale down.
                # Since Phase 3 asks to invest 100% on Long signals, we should have calculated 
                # the quantity correctly prior to this step, so we'll assert.
                if self.cash < 0:
                    raise ValueError(f"Negative cash before buy: {self.cash}")
                # Adjust quantity slightly due to floating point or fees exactly wiping out cash
                order.quantity = self.cash / fill_price
                cost = order.quantity * fill_price
                
            self.cash -= cost
            
            if pos is None:
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    average_entry_price=fill_price,
                    side=1,
                    entry_timestamp=fill_timestamp
                )
            else:
                # Average up/down
                total_cost = (pos.quantity * pos.average_entry_price) + cost
                new_qty = pos.quantity + order.quantity
                pos.average_entry_price = total_cost / new_qty
                pos.quantity = new_qty
                
        elif order.side <= 0:
            # Sell / Close position
            if pos is None:
                # Nothing to close
                return
                
            close_qty = pos.quantity if order.quantity == 0 else min(order.quantity, pos.quantity)
            revenue = close_qty * fill_price
            self.cash += revenue
            
            # Calculate PnL
            gross_pnl = (fill_price - pos.average_entry_price) * close_qty
            # To be perfectly precise, we should attribute entry fees to the trade as well.
            # For simplicity, we attribute the exit fee entirely here.
            net_pnl = gross_pnl - fee
            
            # Create Trade record
            trade = Trade(
                id=str(uuid.uuid4()),
                symbol=order.symbol,
                entry_timestamp=pos.entry_timestamp,
                exit_timestamp=fill_timestamp,
                entry_price=pos.average_entry_price,
                exit_price=fill_price,
                quantity=close_qty,
                side=pos.side,
                fees=fee,  # we only track exit fee in this simple trade record
                net_pnl=net_pnl,
                return_pct=(fill_price - pos.average_entry_price) / pos.average_entry_price,
                strategy_id=strategy_id
            )
            self.trades.append(trade)
            
            pos.quantity -= close_qty
            if pos.quantity <= 1e-6: # Float precision
                del self.positions[order.symbol]

    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio equity (cash + position market value).
        """
        equity = self.cash
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                equity += pos.quantity * current_prices[symbol]
            else:
                equity += pos.quantity * pos.average_entry_price # Fallback
        return equity
