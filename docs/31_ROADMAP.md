# 31 — Roadmap

| Field | Value |
|---|---|
| **Document ID** | RM-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Implementation Plan](./29_IMPLEMENTATION_PLAN.md), [MVP Scope](./03_MVP_SCOPE.md) |

---

## 1. MVP Roadmap

```mermaid
gantt
    title MVP Development Roadmap
    dateFormat  YYYY-MM-DD
    todayMarker off

    section Foundation
    Phase 0 - Documentation       :done, p0, 2026-08-15, 1d
    Phase 1 - Project Setup       :p1, after p0, 5d
    Phase 2 - Data Abstraction    :p2, after p1, 5d
    Phase 3 - Data Ingestion      :p3, after p2, 7d

    section Data Layer
    Phase 4 - Database Schema     :p4, after p1, 5d

    section Core Engine
    Phase 5 - Features            :p5, after p3, 10d
    Phase 6 - Strategies          :p6, after p5, 10d
    Phase 7 - Backtesting         :p7, after p6, 10d
    Phase 8 - Analytics           :p8, after p7, 10d

    section ML & Intelligence
    Phase 9 - ML Ranking          :p9, after p8, 10d
    Phase 10 - Sentiment          :p10, after p4, 10d
    Phase 11 - Fundamentals       :p11, after p4, 7d
    Phase 12 - AI Chatbot         :p12, after p9, 10d

    section Platform
    Phase 13 - API                :p13, after p8, 10d
    Phase 14 - Frontend           :p14, after p13, 15d

    section Quality & Deployment
    Phase 15 - Testing            :p15, after p14, 7d
    Phase 16 - Deployment         :p16, after p15, 5d
```

> [!NOTE]
> The timeline is illustrative. Actual dates depend on team size, provider selection, and client feedback. Many phases can be parallelized with a larger team.

---

## 2. Milestones

| Milestone | Description | Dependencies |
|---|---|---|
| **M1: Data Pipeline** | Historical data can be ingested, validated, and stored | Phase 1-4 |
| **M2: Feature Engine** | All feature categories implemented and tested | Phase 5 |
| **M3: Strategy Engine** | All strategy families implemented with backtest support | Phase 6-7 |
| **M4: Analytics Complete** | Full metrics, optimization, and walk-forward validation | Phase 8 |
| **M5: ML Ranking** | Strategy ranking model trained and evaluated | Phase 9 |
| **M6: Intelligence** | Sentiment, fundamentals, and chatbot operational | Phase 10-12 |
| **M7: API Complete** | All REST endpoints implemented and tested | Phase 13 |
| **M8: Dashboard** | Web dashboard functional | Phase 14 |
| **M9: MVP Complete** | All tests pass; deployment complete | Phase 15-16 |

---

## 3. Phase 2 Roadmap (Post-MVP)

| Feature | Estimated Timeline |
|---|---|
| Paper trading simulation | After MVP + 2-4 weeks |
| Live data streaming | After provider confirmation + 2-3 weeks |
| Multi-user authentication | 2-3 weeks |
| Broker integration interface | 3-4 weeks |
| Enhanced ML models | 2-3 weeks |
| Alerting system | 1-2 weeks |

---

## 4. Phase 3 Roadmap (SaaS)

| Feature | Prerequisites |
|---|---|
| Multi-tenant architecture | Phase 2 auth; database isolation design |
| Billing and subscription | Tenancy model; payment integration |
| Advanced risk management | Live trading; regulatory review |
| Mobile application | Stable API; design investment |

---

## 5. Cross-References

| Document | Relevance |
|---|---|
| [Implementation Plan](./29_IMPLEMENTATION_PLAN.md) | Detailed phase tasks |
| [MVP Scope](./03_MVP_SCOPE.md) | What's in MVP vs future |
| [Tasks](./30_TASKS.md) | Task checklist |
