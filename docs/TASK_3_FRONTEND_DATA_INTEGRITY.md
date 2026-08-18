# TASK 3: FRONTEND DATA INTEGRITY AUDIT & FIXES

## 1. Hardcoded Data Removed
- `2450.0` mock price in `SignalCenter` when approving/ignoring opportunities. Replaced with dynamic `opp.entry_price` / `opp.target_price`.
- "NEWS SOURCE: MOCK" and "DATA SOURCE: UPSTOX / MOCK" strings in `SignalCenter`. Replaced with dynamic AI Provider source logic.
- Max Drawdown mock static value safely defaulted to `NO DATA` if missing.
- Static "Market Regime" block in `Dashboard` safely updated to reflect `NO DATA` as regime is not currently supplied directly by the active portfolio/signal backend.
- Replaced raw HTTP static backend host strings (`http://localhost:8000/...`) in Research and Experiments dashboards with the authenticated `api` proxy utility.

## 2. Mock Data Removed
- Replaced API blind-bypassing in Experiments dashboard. `createExperiment` now correctly connects using Next.js proxy instead of raw fetches.
- Replaced mock `fetch` bypasses in Operations dashboard for `/operations/status` and `/operations/incidents` endpoints.

## 3. Intentional Mock Data Retained
- The `generateMockOpportunity()` developer tool remains available but is visibly distinct. 
- "NO OPPORTUNITIES", "NO POSITIONS", "NO BACKTEST RESULT" explicitly added.

## 4. APIs Connected
- Added `getOperationsStatus`, `getOperationsHealth`, `getProvidersHealth`, `getMarketDataHealth`, `getHeartbeats`, `getIncidents`.
- Added `getResearchSummary`, `getCurrentSession`, `getDailyReport`, `manageSession`.
- Added `getExperiments`, `getExperiment`, `createExperiment`.
- Unified all under `frontend/src/lib/api.ts`.

## 5. Frontend Pages Audited
- `app/page.tsx` (Dashboard)
- `app/portfolio/page.tsx` (Paper Portfolio)
- `app/signals/page.tsx` (Signal Center)
- `app/strategies/page.tsx` (Strategy Studio)
- `app/backtesting/page.tsx` (Backtesting)
- `app/research/page.tsx` (Research)
- `app/operations/page.tsx` (Operations)
- `app/experiments/page.tsx` (Experiments)

## 6. Build Result
- **PASS**: 0 Errors, 0 Warnings via `npm run build`. Fixed Next.js 15 route handler parameter promise typing issue.

## 7. Backend Test Result
- **PASS**: 99 Passed, 0 Failed via `pytest tests/`.

## 8. Security Result
- `MARKET_API_TOKEN` is strictly consumed in `route.ts` (Next.js Node proxy).
- It is NEVER exposed with the `NEXT_PUBLIC_` prefix.
- Client browser receives only proxy routing.

## 9. Paper-only Result
- `EXECUTION: PAPER ONLY` and `LIVE: LOCKED` permanently enforced and visible on the dashboard header.
- No live-trading configurations exist or can be activated.

## 10. Files Changed
- `frontend/src/lib/api.ts`
- `frontend/src/app/page.tsx`
- `frontend/src/app/portfolio/page.tsx`
- `frontend/src/app/signals/page.tsx`
- `frontend/src/app/strategies/page.tsx`
- `frontend/src/app/backtesting/page.tsx`
- `frontend/src/app/research/page.tsx`
- `frontend/src/app/operations/page.tsx`
- `frontend/src/app/experiments/page.tsx`
- `frontend/src/app/api/[...path]/route.ts`
- `docs/TASK_3_FRONTEND_DATA_INTEGRITY.md`
