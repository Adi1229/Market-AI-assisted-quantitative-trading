# 33 — Open Questions

| Field | Value |
|---|---|
| **Document ID** | OQ-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft — Requires Client Input |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [PRD](./01_PRODUCT_REQUIREMENTS_DOCUMENT.md), [MVP Scope](./03_MVP_SCOPE.md) |

---

## Purpose

This document captures all unresolved questions that were identified during requirements analysis and documentation generation. These questions must **not** be silently answered by the architecture team. Each question should be reviewed and answered by the client or project stakeholders before the affected component is implemented.

---

## Question Status Legend

| Status | Meaning |
|---|---|
| 🔴 OPEN | Requires client input before implementation |
| 🟡 PROPOSED | Architecture team has a proposed default; awaiting confirmation |
| 🟢 RESOLVED | Answered by client |

---

## 1. Market Data & Providers

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-MD-001 | Which market-data provider should be used for the MVP? DhanHQ is mentioned as an example — is it confirmed? | 🟡 PROPOSED | Design provider-agnostic interface; implement DhanHQ adapter as first candidate | Affects data ingestion implementation |
| OQ-MD-002 | What API subscription level/tier will be available? | 🔴 OPEN | — | Affects rate limits, data depth, historical availability |
| OQ-MD-003 | What historical data depth is required? (e.g., 1 year, 5 years, 10+ years) | 🔴 OPEN | — | Affects storage sizing and ingestion time |
| OQ-MD-004 | Is real-time streaming data required for the MVP, or is periodic polling sufficient? | 🟡 PROPOSED | Periodic polling / delayed data for MVP | Affects infrastructure complexity |
| OQ-MD-005 | What specific intraday timeframes are required? (1m, 5m, 15m, 30m, 1h, etc.) | 🔴 OPEN | — | Affects data volume and storage |
| OQ-MD-006 | Does the data provider handle corporate action adjustments, or must the platform handle them independently? | 🔴 OPEN | — | Affects data processing pipeline |

---

## 2. Instrument Universe

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-IU-001 | What is the exact instrument universe? All NSE equities? BSE? Both? | 🟡 PROPOSED | NSE equities as starting point | Affects data volume and storage |
| OQ-IU-002 | Which specific Indian indices should be supported? | 🟡 PROPOSED | NIFTY 50, NIFTY Bank as initial candidates | Affects index data ingestion |
| OQ-IU-003 | Should F&O (Futures & Options) instruments be supported? | 🔴 OPEN | — | Significantly affects data model |
| OQ-IU-004 | How should delisted securities be handled for survivorship bias? | 🟡 PROPOSED | Include if data provider supports historical delisted data | Affects data completeness |

---

## 3. News & Sentiment

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-NS-001 | Which news data provider should be used? | 🔴 OPEN | Design provider-agnostic interface; evaluate candidates during implementation | Affects sentiment pipeline |
| OQ-NS-002 | Is a specific NLP sentiment model preferred (e.g., FinBERT, custom, API-based)? | 🟡 PROPOSED | Start with pre-trained financial sentiment model (e.g., FinBERT) | Affects ML infrastructure |
| OQ-NS-003 | What news sources should be covered? (e.g., Indian financial news, global financial news, social media) | 🔴 OPEN | — | Affects provider selection |
| OQ-NS-004 | What is the required news history depth for backtesting? | 🔴 OPEN | — | Affects feasibility of sentiment backtesting |

---

## 4. Fundamental Data

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-FA-001 | Which fundamental data provider should be used? | 🔴 OPEN | Design provider-agnostic interface; evaluate candidates | Affects implementation |
| OQ-FA-002 | Is point-in-time fundamental data available from the provider, or must the platform reconstruct it? | 🔴 OPEN | — | Significantly affects data reliability for backtesting |
| OQ-FA-003 | What frequency of fundamental data updates is expected? (quarterly, annual, ad-hoc) | 🟡 PROPOSED | Quarterly aligned with Indian reporting periods | Affects update pipeline |

---

## 5. AI / LLM

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-AI-001 | Which LLM provider should be used? (OpenAI, Anthropic, Google, open-source, etc.) | 🔴 OPEN | Design LLM-agnostic interface | Affects cost, latency, data privacy |
| OQ-AI-002 | Are there data privacy constraints on sending market/financial data to external LLM APIs? | 🔴 OPEN | — | May require self-hosted models |
| OQ-AI-003 | Which embedding model should be used for vector search? | 🟡 PROPOSED | Evaluate: OpenAI embeddings, sentence-transformers, provider-specific | Affects RAG quality and cost |
| OQ-AI-004 | Which vector database should be used? | 🟡 PROPOSED | pgvector for MVP simplicity; dedicated vector DB if scale demands | Affects infrastructure |
| OQ-AI-005 | What is the budget allocation for LLM API costs? | 🔴 OPEN | — | Affects model selection and usage limits |

---

## 6. Authentication & Users

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-AU-001 | Is the MVP single-user or multi-user? | 🟡 PROPOSED | Single-user for MVP; multi-user path documented | Affects auth, DB isolation, API design |
| OQ-AU-002 | What authentication mechanism is required? (API key, OAuth, SSO, etc.) | 🟡 PROPOSED | API key authentication for MVP | Affects security design |
| OQ-AU-003 | Are there role-based access control requirements? | 🔴 OPEN | — | Affects authorization design |

---

## 7. Trading & Execution

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-TR-001 | Is paper trading required for the MVP? | 🟡 PROPOSED | Not in MVP; documented as Phase 2 | Affects scope |
| OQ-TR-002 | Which broker(s) should be supported for future integration? | 🔴 OPEN | — | Affects broker provider interface |
| OQ-TR-003 | Are there specific regulatory compliance requirements (SEBI, etc.)? | 🔴 OPEN | — | May affect platform design |

---

## 8. Deployment & Infrastructure

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-DE-001 | Which AWS region should be used? | 🟡 PROPOSED | ap-south-1 (Mumbai) for low latency to Indian markets | Affects deployment config |
| OQ-DE-002 | Is there an existing AWS account/infrastructure? | 🔴 OPEN | — | Affects deployment planning |
| OQ-DE-003 | What is the deployment budget? | 🔴 OPEN | — | Affects infrastructure sizing |
| OQ-DE-004 | Are there specific CI/CD tool preferences? | 🟡 PROPOSED | GitHub Actions | Affects CI/CD setup |
| OQ-DE-005 | What is the expected data volume and growth rate? | 🔴 OPEN | — | Affects storage and partitioning strategy |

---

## 9. Scale & Performance

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-SC-001 | How many instruments should the MVP support? | 🟡 PROPOSED | ~500 NSE equities (assumption, not confirmed) | Affects performance, storage |
| OQ-SC-002 | How many concurrent users should be supported? | 🟡 PROPOSED | Single user for MVP | Affects infrastructure |
| OQ-SC-003 | What is the expected backtest execution time tolerance? | 🔴 OPEN | — | Affects engine architecture |

---

## 10. SaaS & Multi-Tenancy

| ID | Question | Status | Proposed Default | Impact |
|---|---|---|---|---|
| OQ-SA-001 | What is the target SaaS tenancy model? (shared DB, isolated DB, schema-per-tenant) | 🔴 OPEN | — | Affects future database architecture |
| OQ-SA-002 | When is SaaS capability expected to be needed? | 🔴 OPEN | — | Affects current architectural decisions |
| OQ-SA-003 | What billing/subscription model is envisioned? | 🔴 OPEN | — | Affects feature gating design |

---

## Resolution Process

1. Questions are raised during documentation or implementation
2. Questions are logged in this document with a proposed default where applicable
3. Client reviews and provides answers
4. Resolved questions are marked 🟢 with the client's answer recorded
5. Implementation proceeds based on resolved answers or proposed defaults (with explicit documentation that the default was used)

---

## Cross-References

| Document | Relevance |
|---|---|
| [PRD](./01_PRODUCT_REQUIREMENTS_DOCUMENT.md) | Requirements affected by open questions |
| [MVP Scope](./03_MVP_SCOPE.md) | Scope decisions affected by open questions |
| [Architecture Decisions](./32_ARCHITECTURE_DECISIONS.md) | ADRs that depend on question resolution |
| [Assumptions (PRD §14)](./01_PRODUCT_REQUIREMENTS_DOCUMENT.md#14-assumptions) | Assumptions derived from proposed defaults |
