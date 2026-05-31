# Test Coverage Report

## Summary

| | Before | After |
|---|---|---|
| Test files | 5 | 11 |
| Tests | 5 | 30 |
| Shared fixtures | none | `tests/conftest.py` |
| Offline / hermetic | partial | yes (`LLM_PROVIDER=echo` set in conftest) |

All 30 pass offline with no cloud credentials, no network, and no model
downloads for inference.

## conftest.py

- Sets `LLM_PROVIDER=echo` and `LANGFLOW_URL=""` **before** any app import, so the
  whole suite is deterministic and offline.
- `client` fixture (TestClient) and an autouse `reset_state` fixture that clears
  competitors and stops any TORCS stream between tests for isolation.

## New tests

| File | Covers |
|------|--------|
| `test_llm_providers.py` | Echo determinism; selector skips unavailable, falls back on error, appends terminal echo; factory auto/explicit/unknown → echo |
| `test_rag.py` | Real retrieval + citations; `ask()` returns `str`; grounding guard on empty retrieval |
| `test_orchestration.py` | LangFlow disabled w/o URL; in-process FIA + explainability; LangFlow path used when available; fallback when empty |
| `test_torcs.py` | SCR parse/field-map/encode; seeded simulator bounds-valid (+ negative-tire-wear regression); ingestor feeds telemetry/competitors/broadcasts |
| `test_api_endpoints.py` | RAG response shape (additive citations/grounded); explain never 500s; competitors POST/GET; TORCS start/stop; websocket broadcast received |

## Preserved

The original 5 tests (`test_health`, `test_telemetry`, `test_strategy`,
`test_simulation`, `test_explanation`) are unchanged and still pass —
confirming backward compatibility of API contracts and response shapes.

## Run

```bash
cd backend
LLM_PROVIDER=echo python -m pytest tests/ -q
# 30 passed
```

## Gaps / not covered (honest)

- **Live provider calls** (watsonx/replicate/ollama) — not exercised; only the
  echo + selection/fallback logic is tested (SDKs absent, no creds).
- **Live LangFlow round-trip** — only the client + fallback via a fake client.
- **TORCS streaming through the HTTP/WebSocket stack** — verified at the
  component/ingestor level; the `TestClient` portal deadlocks on
  `create_task`+blocking receive (harness artifact). Start/stop endpoints are
  tested.
- **Coverage %** — `pytest-cov` is not installed; counts are by test, not line
  coverage. Strategy/simulation engines are intentionally untested here (out of
  scope, owned elsewhere).
