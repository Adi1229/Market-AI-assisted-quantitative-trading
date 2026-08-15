import pandas as pd
import numpy as np
from typing import List, Dict, Any
from app.backtesting.models import Trade

def calculate_metrics(equity_curve: List[Dict[str, Any]], trades: List[Trade], initial_capital: float) -> Dict[str, float]:
    """
    Calculate performance metrics from the equity curve and trade ledger.
    """
    if not equity_curve:
        return {}
        
    df = pd.DataFrame(equity_curve)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    
    final_equity = float(df["equity"].iloc[-1])
    
    # Total Return
    total_return = (final_equity / initial_capital) - 1.0
    
    # CAGR
    days = (df.index[-1] - df.index[0]).days
    if days > 0:
        cagr = ((final_equity / initial_capital) ** (365.25 / days)) - 1.0
    else:
        cagr = 0.0
        
    # Daily returns
    df["daily_return"] = df["equity"].pct_change().fillna(0.0)
    
    # Sharpe Ratio (annualized, assuming 252 trading days)
    daily_returns_std = df["daily_return"].std()
    if daily_returns_std > 0:
        sharpe_ratio = (df["daily_return"].mean() / daily_returns_std) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0
        
    # Sortino Ratio
    negative_returns = df[df["daily_return"] < 0]["daily_return"]
    neg_std = negative_returns.std()
    if len(negative_returns) > 1 and neg_std > 0:
        sortino_ratio = (df["daily_return"].mean() / neg_std) * np.sqrt(252)
    else:
        sortino_ratio = float('inf') if df["daily_return"].mean() > 0 else 0.0
        
    # Max Drawdown
    max_drawdown = float(df["drawdown"].max())
    
    # Trade statistics
    num_trades = len(trades)
    if num_trades > 0:
        winning_trades = [t for t in trades if t.net_pnl > 0]
        losing_trades = [t for t in trades if t.net_pnl <= 0]
        
        win_rate = len(winning_trades) / num_trades
        
        gross_profit = sum(t.net_pnl for t in winning_trades)
        gross_loss = abs(sum(t.net_pnl for t in losing_trades))
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
        
        avg_trade_return = sum(t.return_pct for t in trades) / num_trades
    else:
        win_rate = 0.0
        profit_factor = 0.0
        avg_trade_return = 0.0
        
    return {
        "total_return": total_return,
        "cagr": cagr,
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "num_trades": float(num_trades),
        "avg_trade_return": float(avg_trade_return)
    }
