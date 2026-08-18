with open('docs/PHASE_11C_FRESH_PAPER_EXECUTION_VERIFICATION.md', 'a') as f:
    f.write('''
## Fresh Signal Generation Fix

- **Root Cause**: The validation script was blindly selecting `signals[-1]` regardless of whether that signal pertained to the current candle or a candle from 50 minutes ago. Since the strategy continuously operates over the whole dataframe but only emits entry events when thresholds are actively crossed, taking the last signal submitted an outdated signal to the RiskEngine, guaranteeing a `STALE_SIGNAL` rejection on every run. Furthermore, the `UpstoxMarketDataProvider` provides the *currently forming* candle in its historical results, which was being evaluated as if it were complete.
- **Strategy Evaluation Behavior**: The `MomentumStrategy` correctly calculates conditions (Close > SMA and RSI > Threshold) and strictly yields entry event signals when met. If the current candle does not meet the conditions, no signal is generated.
- **Latest-Candle Handling**: The validation script was updated to drop the *currently forming* candle if `current_time` is less than `candle_timestamp + timeframe`. It then strictly compares the timestamp of the last generated signal against the timestamp of the *latest completed* candle. If they don't match, the strategy evaluation is officially declared FLAT/NO SIGNAL for the current timeframe.
- **Timestamp Semantics**: A 5-minute candle timestamped `05:55:00` represents the `05:55` to `06:00` period and is only "completed" at `06:00:00`.
- **Regression Tests**: Added `test_strategy_signal_timestamp`, `test_strategy_ignores_flat_candles`, and `test_no_future_data` to ensure the strategy maintains its sequential evaluation logic without look-ahead bias and that signal timestamps map exactly to the triggering candle. All tests passed (78/78).
- **Real-Market Validation**: Ran validation against Upstox 5-minute data. At `06:02` UTC, the `06:00` candle was actively forming and was correctly dropped. The strategy evaluated the latest completed `05:55` candle.
- **Fresh Signal**: The `05:55` candle generated NO SIGNAL (FLAT). Therefore, no fresh actionable signal was produced.
- **Paper Execution, Persistence, Duplicate Protection, Restart Persistence**: DEFERRED. Because the strategy did not generate a fresh signal, execution was not triggered, safely halting the workflow exactly as intended for a flat market state.
- **LIVE Safety**: VERIFIED. Execution Mode = PAPER, Broker API calls = 0, Upstox order API calls = 0. No real money transaction occurred.
''')
