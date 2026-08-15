# 24 — Configuration and Environment Management

| Field | Value |
|---|---|
| **Document ID** | CFG-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Security Design](./19_SECURITY_DESIGN.md), [Deployment Architecture](./22_DEPLOYMENT_ARCHITECTURE.md), [Architecture](./05_ARCHITECTURE.md) |

---

## 1. Configuration Layers

| Layer | Source | Priority (highest first) | Examples |
|---|---|---|---|
| **Environment Variables** | OS / container env | 1 (highest) | `DATABASE_URL`, API keys, secrets |
| **Environment File** | `.env` (local only) | 2 | Local development overrides |
| **Config Files** | `configs/*.yaml` | 3 | Application settings, feature flags |
| **Defaults** | Code defaults | 4 (lowest) | Hardcoded fallback values |

> [!IMPORTANT]
> **CLIENT-CONFIRMED:** API keys and secrets must never be stored in source code. `.env` files must never be committed to version control.

---

## 2. Configuration Categories

### 2.1 Secrets (Environment Variables Only)

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | If Redis is used |
| `MARKET_DATA_API_KEY` | Market data provider API key | Yes |
| `NEWS_API_KEY` | News provider API key | If news provider configured |
| `FUNDAMENTAL_API_KEY` | Fundamental data provider API key | If fundamental provider configured |
| `LLM_API_KEY` | LLM provider API key | If LLM is configured |
| `SECRET_KEY` | Application secret key (JWT, etc.) | Yes |

### 2.2 Application Configuration (`configs/app.yaml`)

```yaml
app:
  name: "Market Analysis Platform"
  version: "0.1.0"
  environment: "development"  # development, staging, production
  debug: true
  log_level: "INFO"

api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:3000"]
  rate_limit:
    enabled: true
    requests_per_minute: 60

database:
  pool_size: 10
  pool_timeout: 30
  echo_sql: false
```

### 2.3 Provider Configuration (`configs/providers.yaml`)

```yaml
providers:
  market_data:
    active: "dhan"  # or other provider key; TBD
    # Provider-specific settings loaded at runtime

  news:
    active: null  # TBD

  fundamentals:
    active: null  # TBD

  llm:
    active: null  # TBD
    default_model: null  # TBD
    default_temperature: 0.0
    max_tokens: 2048

  embedding:
    active: null  # TBD
    dimension: null  # TBD
```

### 2.4 Feature Engineering Configuration (`configs/features.yaml`)

```yaml
features:
  default_lookback_buffer: 50  # Extra bars for lookback
  enabled_categories:
    - trend
    - momentum
    - volatility
    - volume
    - price_action
    - statistical
    - regime
```

### 2.5 Backtesting Configuration (`configs/backtesting.yaml`)

```yaml
backtesting:
  default_transaction_costs:
    commission_pct: 0.001   # 0.1% per trade (configurable)
    slippage_pct: 0.0005    # 0.05% slippage (configurable)
    stt_pct: 0.001          # Securities Transaction Tax
    gst_pct: 0.18           # GST on brokerage
    stamp_duty_pct: 0.00015 # Stamp duty

  default_position_sizing:
    method: "equal_weight"
    max_position_pct: 0.10  # 10% max per position

  optimization:
    method: "grid_search"
    max_iterations: 1000
```

### 2.6 Trading Safety Configuration (`configs/safety.yaml`)

```yaml
safety:
  mode: "research"  # research, paper, live (MVP: research only)

  kill_switch:
    enabled: true

  limits:
    max_position_pct: 0.20       # Max 20% in one position
    max_daily_loss_pct: 0.05     # Max 5% daily loss
    max_order_value: null        # TBD
    max_exposure_pct: 1.0        # Max 100% exposure

  live_trading:
    enabled: false               # Must be explicitly enabled
    require_confirmation: true   # Require explicit confirmation
```

---

## 3. Environment-Specific Overrides

| Environment | Config File | Characteristics |
|---|---|---|
| **Development** | `configs/env/development.yaml` | Debug on; verbose logging; local database; mock providers available |
| **Testing** | `configs/env/testing.yaml` | Test database; mock providers; deterministic seeds |
| **Staging** | `configs/env/staging.yaml` | Production-like; separate database; real providers |
| **Production** | `configs/env/production.yaml` | Debug off; structured logging; production database |

---

## 4. Feature Flags

| Flag | Description | Default | Phase |
|---|---|---|---|
| `ENABLE_LIVE_TRADING` | Enable live trading (requires explicit confirmation) | `false` | Phase 2+ |
| `ENABLE_PAPER_TRADING` | Enable paper trading simulation | `false` | Phase 2 |
| `ENABLE_ML_RANKING` | Enable ML strategy ranking | `true` | MVP |
| `ENABLE_CHATBOT` | Enable AI chatbot | `true` | MVP |
| `ENABLE_SENTIMENT` | Enable news sentiment analysis | `true` | MVP |
| `ENABLE_FUNDAMENTALS` | Enable fundamental analysis | `true` | MVP |

---

## 5. `.gitignore` Requirements

```gitignore
# Secrets — MUST NOT be committed
.env
.env.*
*.pem
*.key

# Provider credentials
configs/secrets/

# Local development
*.db
*.sqlite3

# IDE
.vscode/
.idea/

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/
.next/

# ML artifacts (large files)
models/artifacts/
*.pkl
*.joblib
```

---

## 6. Configuration Loading Pattern

```python
# Conceptual pattern — not implementation code
class Settings:
    """Application settings loaded from config files and environment."""

    def __init__(self):
        # Load config files (lowest priority)
        self._config = self._load_yaml_configs()

        # Override with environment variables (highest priority)
        self._apply_env_overrides()

    def _load_yaml_configs(self) -> dict:
        base = load_yaml("configs/app.yaml")
        env_override = load_yaml(f"configs/env/{self.environment}.yaml")
        return deep_merge(base, env_override)

    @property
    def database_url(self) -> str:
        return os.environ["DATABASE_URL"]  # Always from env

    @property
    def environment(self) -> str:
        return os.environ.get("APP_ENV", "development")
```

---

## 7. Cross-References

| Document | Relevance |
|---|---|
| [Security Design](./19_SECURITY_DESIGN.md) | Secrets management details |
| [Deployment Architecture](./22_DEPLOYMENT_ARCHITECTURE.md) | Environment configuration in deployment |
| [Backtesting Engine](./11_BACKTESTING_ENGINE.md) | Transaction cost configuration |
| [Provider Abstraction](./25_DATA_PROVIDER_ABSTRACTION.md) | Provider configuration |
