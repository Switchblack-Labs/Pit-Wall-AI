# Granite Migration Report

## Goal

Make IBM Granite the primary reasoning model via a swappable provider
abstraction, while preserving a working fallback so the system runs with **zero
credentials**.

## Before

- The only real LLM call was `langchain_groq.ChatGroq` hard-wired in
  `app/rag/rag_chain.py` (`llama-3.3-70b-versatile`).
- "Granite" was a fake: `app/clients/granite_client.py` f-string-formatted a
  string; a second `app/integrations/granite_client.py` was empty.

## After — provider abstraction (`app/llm/`)

```
GraniteProvider (ABC: generate / agenerate / is_available)
├── WatsonXProvider          (ibm-watsonx-ai;  WATSONX_API_KEY/PROJECT_ID/URL)
├── ReplicateGraniteProvider (replicate;       REPLICATE_API_TOKEN)
├── OllamaGraniteProvider    (local HTTP;       OLLAMA_BASE_URL, no key)
└── EchoProvider             (offline, deterministic — always available)

AutoProviderSelector  → first available candidate, ordered runtime fallback
factory.get_llm_provider() → cached singleton from Settings
```

### Selection

- `LLM_PROVIDER=auto` (default): try `LLM_FALLBACK_ORDER`
  (`watsonx,replicate,ollama,echo`), pick the first whose creds/endpoint are
  present.
- `LLM_PROVIDER=<name>`: use that provider, still wrapped so an unavailable
  choice degrades to echo instead of crashing.
- On a **generation-time error**, the selector transparently falls through to
  the next candidate; the terminal `echo` provider cannot fail.

### Design choices

- **Lazy SDK imports** — `ibm-watsonx-ai` and `replicate` are imported only when
  their provider is actually used, so they stay optional (commented in
  `requirements.txt`). Missing SDK → `is_available()` returns `False`, never an
  ImportError.
- **Sync + async** — `generate()` is sync; `agenerate()` offloads to a thread via
  `anyio` so FastAPI handlers never block the event loop.
- **Modular/swappable** — adding a provider is one new file + one factory branch.

## Consumers migrated

| Consumer | Before | After |
|----------|--------|-------|
| FIA RAG (`rag_chain.py`) | ChatGroq | `get_llm_provider()` |
| Explainability (`granite_client.py`) | fake string | real Granite prompt + template fallback |
| Orchestration workflows | n/a | use the above |

`GraniteClient`'s public contract (`GraniteClient()` + `await
explain_strategy(...)`) was preserved so `ExplanationService` was not broken.

## Using real Granite

Set credentials in `.env` (see `.env.example`) and optionally
`LLM_PROVIDER=watsonx|replicate|ollama`. **No code change required.** For
Replicate/watsonx, install the optional SDK (`pip install replicate` /
`ibm-watsonx-ai`).

## Honesty notes

- Real Granite output was **not** exercised in this environment (no cloud creds,
  and `replicate`/`ibm-watsonx-ai` are not installed). The watsonx/replicate
  response-parsing paths are written to the documented SDK response shapes but
  validated only by code review + unit tests with mocked providers, not a live
  call. The echo/auto/fallback logic **is** verified by `tests/test_llm_providers.py`.
- `langchain-groq` remains installed in the venv but is no longer imported by the
  app; it can be removed from the environment.
