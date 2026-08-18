# API Authentication & Access Control

This document describes the API Authentication mechanisms protecting Market 2.0.

## Overview
Market 2.0 uses a strict Bearer Token Authentication mechanism on the backend, while safely proxying frontend Next.js requests to avoid exposing secrets in the browser.

## Configuration
The backend is protected via the `MARKET_API_TOKEN` environment variable.
Update your `backend/.env` file:
```ini
MARKET_API_TOKEN=your-secure-token-here
FRONTEND_URL=http://localhost:3000
```

## Public Endpoints
The following endpoints are **PUBLIC** and do not require authentication:
- `GET /api/v1/health` : Used for liveness checks and basic service discovery.

## Protected Endpoints
**ALL OTHER ENDPOINTS** are strictly protected, including but not limited to:
- `POST /api/v1/opportunities/{id}/approve` (Actionable trade execution)
- `POST /api/v1/opportunities/{id}/ignore`
- `GET /api/v1/portfolio/*`
- `GET /api/v1/operations/*`
- `GET /api/v1/experiments/*`

Any request without a valid token will receive a `401 Unauthorized`.

## Frontend Integration
To prevent the token from leaking in the client-side JavaScript bundle, the frontend accesses a Next.js App Router Proxy at `frontend/src/app/api/[...path]/route.ts`. 
1. The browser makes a request to `http://localhost:3000/api/...`
2. The Next.js server intercepts it, injects the `Authorization: Bearer <TOKEN>`, and forwards it to `http://localhost:8000/api/v1/...`
3. This guarantees the secret token never touches the user's browser.

## Security Considerations
- The API Token is never logged or returned in error payloads.
- The comparison uses `secrets.compare_digest` to prevent timing attacks.
- Cross-Origin Resource Sharing (CORS) is hardened to strictly accept traffic only from the configured `FRONTEND_URL`.
- The RiskEngine and Paper Execution pipelines remain fully sovereign. Authentication strictly limits API invocation; it does not bypass internal position sizing or freshness checks.
