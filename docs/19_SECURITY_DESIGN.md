# 19 — Security Design

| Field | Value |
|---|---|
| **Document ID** | SEC-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Config & Environment](./24_CONFIG_AND_ENVIRONMENT.md), [API Specification](./17_API_SPECIFICATION.md), [Deployment Architecture](./22_DEPLOYMENT_ARCHITECTURE.md) |

---

## 1. Security Principles

| Principle | Source |
|---|---|
| No secrets in source code | CLIENT-CONFIRMED (NFR-005) |
| No `.env` committed to version control | CLIENT-CONFIRMED (NFR-006) |
| Provider credentials never in code | CLIENT-CONFIRMED |
| Input validation on all API endpoints | PROPOSED |
| Defense in depth | PROPOSED |

---

## 2. Secrets Management

### 2.1 Storage

| Environment | Approach |
|---|---|
| **Development** | `.env` file (gitignored) |
| **Staging/Production** | AWS Secrets Manager or SSM Parameter Store (PROPOSED) |
| **CI/CD** | GitHub Actions secrets or equivalent (PROPOSED) |

### 2.2 Secret Types

| Secret | Description | Rotation |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | On credential change |
| `REDIS_URL` | Redis connection string | On credential change |
| `MARKET_DATA_API_KEY` | Market data provider key | Per provider policy |
| `NEWS_API_KEY` | News provider key | Per provider policy |
| `FUNDAMENTAL_API_KEY` | Fundamental data provider key | Per provider policy |
| `LLM_API_KEY` | LLM provider key | Per provider policy |
| `SECRET_KEY` | Application signing key | Periodically |

---

## 3. Authentication

> [!NOTE]
> **PROPOSED DEFAULT:** API key authentication for MVP. Authentication requirements are TBD (see [OQ-AU-001](./33_OPEN_QUESTIONS.md), [OQ-AU-002](./33_OPEN_QUESTIONS.md)).

### 3.1 MVP Authentication

| Aspect | Approach |
|---|---|
| Method | API key in Authorization header |
| Format | `Authorization: Bearer <api_key>` |
| Storage | API keys hashed in database |
| Scope | Full API access with valid key |

### 3.2 Future Authentication (Phase 2+)

| Feature | Phase |
|---|---|
| OAuth 2.0 / OIDC | Phase 2 |
| Role-based access control (RBAC) | Phase 2 |
| Multi-user support | Phase 2 |
| SSO integration | Phase 3 |

---

## 4. Authorization

| Resource | MVP Access Control | Future |
|---|---|---|
| Market data | Any authenticated user | Role-based |
| Backtests | Any authenticated user | User-owned |
| ML models | Any authenticated user | Admin only |
| Chat sessions | Any authenticated user | User-owned |
| System configuration | Any authenticated user | Admin only |

---

## 5. Input Validation

| Layer | Validation |
|---|---|
| **API Layer** | Pydantic models validate request schemas |
| **Business Layer** | Domain-specific validation (parameter ranges, date validity) |
| **Database Layer** | Constraints, foreign keys |

| Threat | Mitigation |
|---|---|
| SQL Injection | Parameterized queries (SQLAlchemy ORM) |
| XSS | Response escaping; Content-Security-Policy headers |
| CSRF | SameSite cookies; CSRF tokens if applicable |
| Path Traversal | Input sanitization; no file path from user input |
| Large payloads | Request size limits |

---

## 6. API Security

| Measure | Implementation |
|---|---|
| HTTPS | TLS termination at load balancer |
| CORS | Configured allowed origins |
| Rate Limiting | Per-endpoint rate limits (see [API Spec](./17_API_SPECIFICATION.md)) |
| Request Logging | Log all API requests (excluding sensitive headers) |
| Error Handling | Never expose stack traces in production |

---

## 7. Data Protection

| Aspect | Approach |
|---|---|
| Database encryption | Encryption at rest (AWS RDS default) |
| Transit encryption | TLS for all connections |
| Backup encryption | Encrypted backups |
| PII handling | MVP likely has minimal PII; document if changes |

---

## 8. Audit Logging

| Event | Logged |
|---|---|
| Authentication attempts | Success/failure, timestamp, IP |
| API requests | Method, endpoint, user, timestamp |
| Data ingestion | Provider, records, timestamp |
| Backtest execution | User, strategy, parameters |
| Configuration changes | What changed, by whom |
| Error events | Full error context |

---

## 9. LLM Data Privacy

> [!WARNING]
> Sending financial data to external LLM APIs may have privacy implications. This needs evaluation based on the chosen LLM provider's data handling policies (see [OQ-AI-002](./33_OPEN_QUESTIONS.md)).

| Concern | Mitigation |
|---|---|
| Sensitive data in LLM prompts | Minimize data sent; avoid sending full datasets |
| LLM provider data retention | Review provider's data policy |
| Prompt injection | Sanitize user inputs before including in LLM prompts |

---

## 10. Cross-References

| Document | Relevance |
|---|---|
| [Config & Environment](./24_CONFIG_AND_ENVIRONMENT.md) | Secrets configuration |
| [API Specification](./17_API_SPECIFICATION.md) | API authentication and rate limiting |
| [Deployment Architecture](./22_DEPLOYMENT_ARCHITECTURE.md) | Infrastructure security |
| [Open Questions](./33_OPEN_QUESTIONS.md) | Auth requirement questions |
