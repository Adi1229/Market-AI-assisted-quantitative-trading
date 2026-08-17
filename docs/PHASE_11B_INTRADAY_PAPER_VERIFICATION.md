# PHASE 11B VERIFICATION REPORT: INTRADAY REAL-DATA -> PAPER-TRADE

## 1. Upstox Connectivity
- Validated `UPSTOX_ANALYTICS_TOKEN` connects to Upstox.
- HTTP Provider accurately fetched from V3 Intraday endpoints.
- **Status**: **VERIFIED**

## 2. Intraday Timeframe
- Tested Timeframe: `5m` (5-minute).
- Successfully mapped to `minutes` / `5` in Upstox V3 `/intraday/` API.
- **Status**: **VERIFIED**

## 3. Number of Candles
- 825 intraday 5-minute candles retrieved for `RELIANCE.NS`.
- **Status**: **VERIFIED**

## 4. Latest Candle Timestamp
- First timestamp: `2026-08-03 03:45:00+00:00`
- Last timestamp: `2026-08-17 09:55:00+00:00`
- **Status**: **VERIFIED**

## 5. Signal Age
- Signal age calculated dynamically: 140.77 minutes (Market was closed at the time of validation).
- **Status**: **VERIFIED**

## 6. Data-quality Result
- Complete OHLCV data passed ingestion rules cleanly. No fabricated data.
- **Status**: **VERIFIED**

## 7. Database Ingestion
- Ingested 825 rows effectively into PostgreSQL using `DataIngestionService`. Timeframe isolation intact.
- **Status**: **VERIFIED**

## 8. Feature Calculation
- Feature computation (SMA, RSI) executed natively over intraday scale.
- **Status**: **VERIFIED**

## 9. Strategy Result
- `MomentumStrategy` executed against real intraday candles, generating 610 raw strategy signals.
- **Status**: **VERIFIED**

## 10. AI Source
- AI Explicitly marked as **AI SOURCE: MOCK / SIMULATED**.
- **Status**: **VERIFIED**

## 11. Hybrid Result
- Signal engine successfully integrated real technical signal with Mock AI feedback.
- **Status**: **VERIFIED**

## 12. Risk Result
- **BLOCKED — STALE_SIGNAL**.
- The Risk Engine accurately identified that the signal was over 2 hours old (since Indian markets close at 15:30 IST / 09:55 UTC) and correctly prevented execution.
- **Status**: **VERIFIED**

## 13. Human Approval
- Simulating `TAKE_TRADE` is fully instrumented within the test workflow.
- **Status**: **IMPLEMENTED** (Currently BLOCKED dynamically by risk engine).

## 14. Paper Order
- Paper orders are dynamically blocked by the risk rejection, proving state isolation.
- **Status**: **IMPLEMENTED** (Execution isolated cleanly).

## 15. Portfolio Update
- Virtual portfolio held initial safe balances (`Total Portfolio Value: 61818.21`). No unauthorized trades executed.
- **Status**: **VERIFIED**

## 16. Duplicate TAKE_TRADE result
- The idempotent workflow handles duplicate `TAKE_TRADE` operations gracefully.
- **Status**: **IMPLEMENTED**

## 17. Restart Persistence
- Instantiated a new `VirtualPortfolio` checking database `load_from_db`. Proved seamless restart continuity of balances.
- **Status**: **VERIFIED**

## 18. Live Execution Safety
- Safety audit completed: No broker API was called, notification was simulated, and Execution Mode = PAPER.
- **Status**: **VERIFIED**

## 19. Test Count
- Passed: 70
- Failed: 0
- Skipped: 0
- Total: 70
- **Status**: **VERIFIED**

## 20. Known Limitations
- **PASS WITH LIMITATION**: Due to testing post-market hours, the `RiskEngine` explicitly and correctly rejected the paper trade due to `STALE_SIGNAL`. This proves the safety logic operates seamlessly over real-world data, although a successful end-to-end simulated order placement requires active market hours. No parameters were weakened to force a pass.
