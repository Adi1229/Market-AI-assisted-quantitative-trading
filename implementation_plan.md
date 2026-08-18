# Final 5% Production-Readiness Validation

This plan outlines the methodology to validate Market 2.0 under real-market conditions and produce the final project audit, exactly as requested.

## User Review Required
> [!IMPORTANT]
> The experiment requires human approval. To satisfy the requirement of not bypassing human approval while still allowing the script to complete an End-to-End test, the script will simulate the Telegram/Dashboard human actor by programmatically invoking `WorkflowOrchestrator.process_approval(opp.opportunity_id, "APPROVED")` after the Risk Engine locks the opportunity in `AWAITING_APPROVAL`. This strictly uses the exact same codepath as a real human click without bypassing the architecture. Please confirm this is acceptable.

## Open Questions
- To ensure we get at least one signal to test execution idempotency and restart persistence, we will run the `MomentumStrategy` with highly sensitive parameters (e.g., `fast_period=2, slow_period=3`) across 5 major symbols. Is this acceptable, or do you prefer to wait organically for a default signal?

## Proposed Changes

### Script Generation

#### [NEW] `backend/scripts/final_production_validation.py`
A comprehensive validation script that will:
1. **Experiment Setup**: Create a `PaperExperimentDB` record for `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `ICICIBANK.NS` at `5m` timeframe.
2. **Real Market Data Collection**: Fetch historical 5-minute data from Upstox, strictly dropping the incomplete current candle.
3. **Strategy Evaluation**: Run the `MomentumStrategy`.
4. **Real OpenRouter Analysis**: For any generated signals, invoke `OpenRouterAIProvider` and record the `actual_model` (e.g., `poolside/laguna-xs-2.1:free`).
5. **Hybrid Decision**: Compute Strategy + AI scores.
6. **Risk Engine**: Route the opportunity through `RiskEngine`.
7. **Human-in-the-Loop**: If it passes Risk, the script will programmatically call the approval webhook to simulate human intervention.
8. **Paper Execution**: Verify the trade executes.
9. **Idempotency Test**: Attempt to approve and execute the identical opportunity twice, asserting the second attempt fails.
10. **Restart Persistence Test**: Close DB connections, re-initialize the portfolio, and assert the state survives.
11. **Performance Metrics**: Calculate and output win rates, P&L (if positions can be closed), and AI reliability metrics.
12. **No-Look-Ahead Audit**: Assert timestamps mathematically.
13. **Security Audit**: Scan repository for `OPENROUTER_API_KEY` leaks.

### Documentation Generation

#### [NEW] `docs/FINAL_PAPER_TRADING_EXPERIMENT_REPORT.md`
Will contain the 29-point executive summary and metrics of the experiment.

#### [MODIFY] `docs/FINAL_PROJECT_AUDIT.md`
Will be updated with the final VERIFIED statuses across all 21 checklist items based on the actual outcome of the script.

## Verification Plan

### Automated Tests
- Run `python -m pytest tests/` (Expected: 0 failures)
- Run `npm run build` (Expected: 0 errors)

### Manual Verification
- Execute `python scripts/final_production_validation.py` and capture the resulting logs and generated markdown reports.
