# TASK 4A: OPENROUTER FREE-MODEL & COST-CONTROL VALIDATION

## 1. Provider & Cost Control Architecture
- **Provider implemented**: `OpenRouterAIProvider` inside `app/intelligence/openrouter_provider.py`
- **Cost Controls Implemented**:
  - `AI_MAX_TOKENS = 1024`
  - `AI_REQUEST_TIMEOUT = 15.0`
  - `AI_MAX_REQUESTS_PER_RUN = 1`
- **Idempotency**: Maintained. The existing `Market 2.0` architecture enforces 1 evaluation per opportunity in the database.
- **Duplicate Keys**: Cleaned. `.env.example` and `config.py` specify exactly one `OPENROUTER_API_KEY`.

## 2. Models Evaluated
Using the OpenRouter API, we extracted the current list of free models (where prompt pricing is exactly 0). Evaluated models included:
- `nvidia/nemotron-3.5-lightning:free` (Selected)
- `google/gemma-4-31b-it:free`
- `openai/gpt-oss-20b:free`
- `cohere/north-mini-code:free`
- `google/gemma-2-9b-it:free` (Returned 404 No endpoints found)
- `meta-llama/llama-3.1-8b-instruct:free` (Returned 404 Unavailable for free)

*Note: `openrouter/free` was explicitly excluded as instructed because it dynamically maps to other models.*

## 3. Exact Model Selected
**`nvidia/nemotron-3.5-lightning:free`**

## 4. Real Connectivity & API Behavior
- **Minimal Connectivity Test (Test 1)**: `200 OK`. The minimal prompt `{"status": "ok"}` successfully returned the correct JSON structure within the 15-second timeout.
- **Grounded Market Test (Test 2)**: The model returned a `200 OK` HTTP status, but failed to generate the large JSON schema. The provider received a response, but it resulted in an empty/malformed text block, throwing `Expecting value: line 1 column 1 (char 0)` in the JSON parser.
- **AI Failure Safety Result**: PASS. The system gracefully handled the JSON failure, logged the `AI_ERROR` incident in PostgreSQL, and returned `API_FAILURE`. 

## 5. Offline Tests
- **Offline test count**: 107 tests across the entire backend suite.
- **Offline failures**: 0 (100% pass rate).

## 6. Frontend Result
- **Frontend build result**: PASS (0 Errors, 0 Warnings).

## 7. Security & Safety
- **AI Source Result**: `OPENROUTER — FAILED` (Correctly labelled as a failure, no mock data was disguised as real inference).
- **Security Audit Result**: NO SECRET LEAK FOUND.
- **Paper Safety Result**: PASS. LIVE execution remains locked, RiskEngine remains mandatory, and human approval is still required.

## 8. Limitations
- The OpenRouter free tier models (specifically `nemotron-3.5-lightning:free`) proved extremely slow or incapable of returning large structured JSON payloads reliably within realistic timeouts. They return `200 OK` but fail to complete the generation block for complex prompts.
- Real structured inference requires an upgraded OpenRouter paid tier (e.g. `google/gemini-2.5-flash`).

## 9. Final Status
- **Final status**: PASS WITH LIMITATION (Cost controls successfully added, AI architecture perfectly fail-closed on malformed JSON, but the selected free model failed the structured schema test).
