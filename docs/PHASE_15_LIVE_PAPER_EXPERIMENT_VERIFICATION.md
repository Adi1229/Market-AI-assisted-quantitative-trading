# Phase 15: Live Paper-Trading Experiment & Strategy Evaluation Verification

## Objectives Completed

1. **Experiment Framework Configuration**:
   - Built a rigorous testing harness designed for long-term tracking of strategies without executing real orders.
   - Designed the `PaperExperimentDB` schema to save and validate active experiments.

2. **Security & Data Honesty (Strictly Audited)**:
   - **LIVE Execution is strictly and permanently disabled**. If an experiment attempts to run with execution mode `LIVE`, the runner logs a fatal error, pauses the experiment, and continues processing others. E2E tests confirm this fail-closed behavior.
   - **Mock AI Provider** is strictly used during the experiment to avoid exposing real LLM keys and preventing any unaccounted real API hits.
   - Timeframe and signal freshness logic prevents back-testing bias and look-ahead bias by aggressively removing incomplete/currently forming candles before they reach strategy engines.

3. **Orchestration Architecture**:
   - `phase15_live_paper_experiment.py` implemented as a single-cycle loop that runs through active experiments.
   - `phase15_long_run_paper_experiment.py` implemented to run infinitely (with 5-minute pauses) to manage state and experiment lifecycle expiration continuously.

4. **Monitoring & Interfaces**:
   - Next.js dashboard created for `/experiments` to allow transparent human observation over experiment parameters, timelines, active models, and real-time statuses.
   - API layer (`experiments.py`) guarantees validation on creation constraints (e.g. `PAPER` mode only).

## Verification Checks

- [x] Tested the `POST /api/v1/experiments/` API against constraints.
- [x] Validated `test_e2e_experiment_flow` passing with robust integration between Risk, Execution, Portfolio, and Orchestration.
- [x] Validated timestamp truncating mechanics for `5m` Upstox candles in `scripts/phase15_live_paper_experiment.py`.

## Next Steps

**Stop**. The user explicitly mandated stopping after Phase 15. The product has reached the end of its required roadmap. The platform can now operate cleanly and safely under real-world, forward-testing, long-run mock environments. No live API trading should ever be allowed on this branch.
