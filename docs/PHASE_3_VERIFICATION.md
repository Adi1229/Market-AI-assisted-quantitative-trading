# Phase 3 Verification

## Architecture & Event Model
The backtesting engine operates on a strict, chronological event loop. The execution architecture bridges vectorized feature calculation with an iterative simulation loop to preserve correctness:
1. **Feature Resolver**: Pre-computes required indicators over the whole dataset cleanly.
2. **Signal Pre-Calculation**: Strategy signals are evaluated over the historically complete `pd.DataFrame`. Due to strict bounds in Phase 2 `features/core.py`, look-ahead bias is structurally impossible.
3. **Event Loop**: Iterates chronologically (Timestamp $t$).
    - Any open orders requested on $t-1$ are immediately filled using the $Open_t$ price. 
    - The Strategy Signal map is checked for signals generated at $t$.
    - New Orders are dispatched for the next timestamp ($t+1$).
    - Portfolio values are marked-to-market at the $Close_t$.

## Execution Convention
- **Order Timing**: End of Bar signals execute at the `open` of the subsequent candle.
- **Sizing Model**: Simplistic Phase 3 model invests 100% of available cash on Long signals. A Flat/Short signal unconditionally closes out the Long position in full.
- **Cash Management**: The portfolio prevents executing trades that would drop the cash balance strictly below zero (handled safely during quantity calculation). 

## Transaction Costs & Slippage
Configurable in `BacktestConfig`:
- **Slippage**: Defined in basis points (bps). A 100 bps slippage increases a buy execution price by 1%.
- **Transaction Costs**: Defined in basis points (bps). Net fees are reduced from cash concurrently with trade executions (fees for exit trades are deducted from sales proceeds).

## Look-Ahead & Reproducibility Validation
- **Test A (No Look-Ahead)**: Explicitly alters future timeframe data within a sample set and validates that historical signal and simulation records perfectly match the unaltered variant.
- **Test G (Reproducibility)**: Re-runs the exact Backtest configuration twice to strictly ensure equivalence across metrics and trade outputs.

## Database & Invariants
- **No Persistence**: The model runs entirely in-memory and outputs `BacktestResult`. No schema changes were made.
- **Preserved constraints**: No broker, AI, Telegram, or backend integrations were built. 

## Test Results
Command run: `python -m pytest tests/`

- **Phase 1 Tests**: 4 passed / 0 failed
- **Phase 2 Tests**: 15 passed / 0 failed
- **Phase 3 Tests**: 8 passed / 0 failed
- **Total**: 27 passed / 0 failed

## Final Status
PASS
