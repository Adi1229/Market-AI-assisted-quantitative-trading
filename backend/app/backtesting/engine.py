import pandas as pd
import uuid
from typing import Dict, Any, List
from app.backtesting.models import BacktestConfig, BacktestResult, Order
from app.backtesting.portfolio import Portfolio
from app.backtesting.metrics import calculate_metrics
from app.strategies.registry import StrategyRegistry
import app.quantitative.features.core as features

class FeatureResolver:
    """
    Resolves a list of required feature names into actual calculations on the DataFrame.
    """
    @staticmethod
    def resolve_and_compute(df: pd.DataFrame, required_features: List[str]) -> pd.DataFrame:
        df = df.copy()
        for feature in required_features:
            if feature in df.columns:
                continue
                
            parts = feature.split('_')
            base = parts[0]
            
            # Very basic parser for expected features
            if base == "SMA" and len(parts) == 2:
                window = int(parts[1])
                df[feature] = features.calculate_sma(df, window=window)
            elif base == "EMA" and len(parts) == 2:
                window = int(parts[1])
                df[feature] = features.calculate_ema(df, window=window)
            elif base == "RSI" and len(parts) == 2:
                window = int(parts[1])
                df[feature] = features.calculate_rsi(df, window=window)
            elif base == "ATR" and len(parts) == 2:
                window = int(parts[1])
                df[feature] = features.calculate_atr(df, window=window)
            elif base == "VOLATILITY" and len(parts) == 2:
                window = int(parts[1])
                df[feature] = features.calculate_volatility(df, window=window)
            elif base == "RETURNS":
                df[feature] = features.calculate_returns(df)
            else:
                raise ValueError(f"Unknown or unsupported feature format: {feature}")
        return df


class BacktestEngine:
    """
    Chronological Event-Driven Backtesting Engine.
    """
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.portfolio = Portfolio(initial_capital=config.initial_capital)
        
    def run(self, df: pd.DataFrame) -> BacktestResult:
        if df.empty:
            raise ValueError("Empty DataFrame provided for backtesting.")
            
        if "open" not in df.columns or "close" not in df.columns:
            raise ValueError("DataFrame must contain 'open' and 'close' columns.")
            
        strategy = StrategyRegistry.get_strategy(self.config.strategy_id, **self.config.strategy_parameters)
        
        # 1. Feature resolution
        df = FeatureResolver.resolve_and_compute(df, strategy.required_features)
        
        # 2. Vectorized signal generation
        #    This is allowed because strategies must strictly enforce no look-ahead bias internally.
        #    We trust the Phase 2 components for this.
        signals = strategy.generate_signals(df)
        
        # Create a mapping of timestamp -> signal for O(1) chronological lookup
        signal_map = {pd.Timestamp(sig.timestamp): sig for sig in signals}
        
        # 3. Chronological Event Loop
        equity_curve = []
        pending_orders: List[Order] = []
        
        # For iteration, it's easiest if timestamp is an explicit column or index.
        # We'll assume the index is datetime or 'timestamp' column exists.
        timestamps = df.index if isinstance(df.index, pd.DatetimeIndex) else df["timestamp"]
        
        # Max peak for drawdown calculations in real-time
        max_equity = self.portfolio.cash
        
        for idx in df.index:
            row = df.loc[idx]
            current_timestamp = idx if isinstance(idx, pd.Timestamp) else row["timestamp"]
            current_open = float(row["open"])
            current_close = float(row["close"])
            
            # Step A: Process pending orders (execute at Open of T)
            new_pending = []
            for order in pending_orders:
                # Calculate execution price with slippage
                # slippage_bps = 5 means 0.0005. 
                # If buying, we pay more. If selling, we receive less.
                slippage_multiplier = 1 + (order.side * (self.config.slippage_bps / 10000.0))
                exec_price = current_open * slippage_multiplier
                
                if order.side == 1 and order.quantity == 0:
                    order.quantity = self.portfolio.cash / exec_price
                
                # Execute if quantity > 0 OR if it's a close all order (side <= 0 and quantity == 0)
                if order.quantity > 0 or (order.side <= 0 and order.quantity == 0):
                    # Calculate fee (e.g. 1 bps on notional value)
                    # For close all, we don't know the exact quantity yet, but portfolio will resolve it.
                    # We'll pass the fee rate instead, or let portfolio calculate the exact fee.
                    # Wait, our current process_fill takes the exact absolute fee!
                    # Let's let process_fill calculate it if order.quantity == 0.
                    # For simplicity, if order.quantity == 0, we can temporarily set it to pos.quantity.
                    if order.quantity == 0 and order.side <= 0:
                        pos = self.portfolio.positions.get(order.symbol)
                        if pos:
                            order.quantity = pos.quantity
                            
                    notional = order.quantity * exec_price
                    fee = notional * (self.config.fee_bps / 10000.0)
                    
                    try:
                        self.portfolio.process_fill(
                            order=order,
                            fill_price=exec_price,
                            fee=fee,
                            fill_timestamp=current_timestamp,
                            strategy_id=strategy.id
                        )
                    except ValueError as e:
                        # Order rejected due to insufficient funds, etc.
                        pass # Silently drop rejected orders in this basic simulation
                        
            pending_orders = new_pending # Clear filled orders
            
            # Step B: Check for new signals generated at Close of T
            print(f"Checking for signal at {current_timestamp}...")
            if current_timestamp in signal_map:
                sig = signal_map[current_timestamp]
                print(f"Signal found: {sig.direction}")
                
                # Convert signal to Order
                # In Phase 3, 1 means Long, -1 means Short, 0 means Flat/Close.
                # However, portfolio currently only supports closing out positions.
                # So -1 (Short) or 0 (Flat) will just close the Long position.
                
                pos = self.portfolio.positions.get(self.config.symbol)
                
                # State machine
                if sig.direction == 1 and pos is None:
                    # Enter Long
                    pending_orders.append(Order(
                        id=str(uuid.uuid4()),
                        symbol=self.config.symbol,
                        timestamp=current_timestamp,
                        side=1,
                        quantity=0, # Auto-size in process_fill
                        strategy_id=strategy.id
                    ))
                    print("Created LONG order")
                elif sig.direction <= 0 and pos is not None:
                    # Close Long
                    pending_orders.append(Order(
                        id=str(uuid.uuid4()),
                        symbol=self.config.symbol,
                        timestamp=current_timestamp,
                        side=-1,
                        quantity=0, # Close all
                        strategy_id=strategy.id
                    ))
                    print("Created CLOSE order")
                    
            # Step C: Mark to Market (at Close of T)
            eq = self.portfolio.get_equity({self.config.symbol: current_close})
            if eq > max_equity:
                max_equity = eq
                
            drawdown = (max_equity - eq) / max_equity if max_equity > 0 else 0
            
            equity_curve.append({
                "timestamp": current_timestamp,
                "equity": eq,
                "drawdown": drawdown
            })
            
        # Compile Results
        metrics = calculate_metrics(equity_curve, self.portfolio.trades, self.config.initial_capital)
        
        return BacktestResult(
            config=self.config,
            metrics=metrics,
            trades=self.portfolio.trades,
            equity_curve=equity_curve
        )
