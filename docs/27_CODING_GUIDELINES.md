# 27 — Coding Guidelines

| Field | Value |
|---|---|
| **Document ID** | CG-001 |
| **Version** | 0.1.0-draft |
| **Status** | Draft |
| **Last Updated** | 2026-08-15 |
| **Related Documents** | [Architecture](./05_ARCHITECTURE.md), [Project Structure](./28_PROJECT_STRUCTURE.md), [Testing Strategy](./20_TESTING_STRATEGY.md) |

---

## 1. Python Standards

### 1.1 General

| Guideline | Standard |
|---|---|
| Python version | 3.11+ |
| Style | PEP 8 |
| Formatter | Black (line length 88) |
| Linter | Ruff |
| Type hints | Required for all function signatures |
| Docstrings | Google style; required for public functions/classes |
| Import order | Standard library → third-party → local (isort) |

### 1.2 Async

| Guideline | Standard |
|---|---|
| Async I/O | Use `async`/`await` for all I/O operations |
| Database | async drivers (asyncpg / SQLAlchemy async) |
| HTTP clients | httpx (async) |
| Background tasks | FastAPI BackgroundTasks or task queue |

### 1.3 Data Classes

| Use Case | Approach |
|---|---|
| API schemas | Pydantic models |
| Internal data | Python dataclasses or Pydantic |
| Database models | SQLAlchemy models |
| Enums | Python Enum (not magic strings) |

---

## 2. Code Organization

### 2.1 Module Structure

Each module should contain:

```
module_name/
├── __init__.py      # Public exports
├── models.py        # Data models for this module
├── service.py       # Business logic
├── repository.py    # Database access
├── interfaces.py    # Abstract interfaces (if applicable)
├── exceptions.py    # Module-specific exceptions
└── utils.py         # Module utilities
```

### 2.2 Dependencies

| Rule | Description |
|---|---|
| Core has no dependencies | `core/` depends on nothing else |
| Layers depend downward only | Services → Repositories → Database |
| No circular imports | Use interfaces to break cycles |
| Provider implementations are isolated | Provider-specific code only in provider classes |

---

## 3. Error Handling

| Pattern | Usage |
|---|---|
| Custom exceptions | Domain-specific exceptions in each module |
| Exception hierarchy | Base → Category → Specific |
| No bare `except` | Always catch specific exceptions |
| Logging | Log errors with context before re-raising |
| API errors | Convert to standardized HTTP error responses |

```python
# Exception hierarchy example
class MarketPlatformError(Exception): ...
class DataError(MarketPlatformError): ...
class ValidationError(DataError): ...
class ProviderError(MarketPlatformError): ...
class ProviderUnavailableError(ProviderError): ...
```

---

## 4. Testing Standards

| Standard | Description |
|---|---|
| Test file naming | `test_<module>.py` |
| Test function naming | `test_<function>_<scenario>` |
| Fixtures | pytest fixtures for setup/teardown |
| Mocks | Mock external dependencies; never mock internal logic |
| Assertions | One assertion concept per test |
| Data | Use factories for test data |

---

## 5. Git Practices

| Practice | Description |
|---|---|
| Branch naming | `feature/`, `fix/`, `docs/`, `refactor/` |
| Commit messages | Conventional commits (`feat:`, `fix:`, `docs:`, `test:`) |
| PR size | Keep PRs focused; < 400 lines changed preferred |
| Reviews | All code must be reviewed before merge |

---

## 6. Documentation

| Level | Requirements |
|---|---|
| **Functions** | Docstring with description, args, returns, raises |
| **Classes** | Docstring with purpose, usage |
| **Modules** | Module-level docstring describing purpose |
| **Configuration** | Inline comments for non-obvious settings |
| **Architecture** | Maintained in `docs/` directory |

---

## 7. Security in Code

| Rule | Description |
|---|---|
| No hardcoded secrets | All secrets from environment variables |
| No `eval()` or `exec()` | Never execute dynamic code |
| Parameterized queries | Always use ORM or parameterized SQL |
| Input validation | Validate all external inputs |
| Dependency scanning | Regular dependency vulnerability checks |

---

## 8. Performance Guidelines

| Guideline | Description |
|---|---|
| Use vectorized operations | Pandas/NumPy for data operations; avoid Python loops |
| Batch database operations | Bulk inserts/updates where possible |
| Connection pooling | Reuse database connections |
| Lazy loading | Load data on demand, not upfront |
| Profiling | Profile before optimizing; measure improvements |

---

## 9. Cross-References

| Document | Relevance |
|---|---|
| [Project Structure](./28_PROJECT_STRUCTURE.md) | Directory layout |
| [Architecture](./05_ARCHITECTURE.md) | Component boundaries |
| [Testing Strategy](./20_TESTING_STRATEGY.md) | Test patterns |
