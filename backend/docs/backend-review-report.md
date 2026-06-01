# Backend Review Report

Scope: backend + AI stack of Pit Wall AI (`/backend`). Frontend and the
strategy/simulation math engine were out of scope (the latter belongs to another
teammate — see "Known limitations").

## Architecture (as found)

Clean layered FastAPI app: `api/` (routers) → `services/` (business logic) →
`state/` (in-memory) + `engine/` + `rag/`. Singletons wired in
`app/dependencies.py`. Real-time updates via a WebSocket broadcast hub
(`/ws/live`). This structure is sound and was preserved; changes were additive.

## What was reviewed and changed

| Area | Finding | Action |
|------|---------|--------|
| LLM inference | Only Groq, hard-wired in `rag/rag_chain.py`; a fake "Granite" string-formatter | Replaced with a swappable `GraniteProvider` abstraction (`app/llm/`); Granite-first with offline fallback |
| FIA RAG | Worked, but no citations, no grounding guard, eager model load | Added citations + grounding guard; lazy vector store; kept retrieval/embeddings/ChromaDB intact |
| Explainability | Stub f-string, no model call | Real Granite prompt + deterministic fallback; never 500s |
| Orchestration | None | Added `app/orchestration/` workflows (source of truth) + optional LangFlow client |
| TORCS | Field-mapping adapter only | Full additive ingestion + simulated source + live stub + endpoints |
| `main.py` | Deprecated `@app.on_event`; duplicate `rag_router` import | Migrated to `lifespan`; removed duplicate |
| Duplicate clients | Empty `integrations/granite_client.py` | Removed |
| `api/ai.py` | Empty, unregistered stub | Confirmed unused; left as-is (no router to register) |
| Config | Deprecated inner `class Config` | Migrated to `SettingsConfigDict` |
| Dependencies | `langchain*`/`chromadb` unpinned; **PyMuPDF + langchain-text-splitters missing** despite being imported | Pinned to installed versions; added the two missing deps |

## Async / WebSocket correctness

- `WebSocketService.broadcast` already prunes dead connections — verified, kept.
- TORCS streaming uses the same fire-and-forget `asyncio.create_task` pattern as
  the demo; both now cancel cleanly on shutdown via the `lifespan` handler.
- `start` endpoints are idempotent (guard on a `running` flag).

## Security note (flagged, not silently changed)

All HTTP/WebSocket endpoints are **unauthenticated** and CORS is fully open
(`allow_origins=["*"]`). This matches the original design and is acceptable for a
hackathon/demo, but is called out in the Deployment Report as the first item to
address before any public, multi-tenant deployment.

## Known limitations (deliberately out of scope)

- **Strategy engine** (`app/engine/strategy_engine.py`) and **simulation engine**
  (`app/engine/scenario_engine.py`) remain **hardcoded stubs** — they ignore
  inputs and return fixed values. These are owned by another team member.
  Integration points are stable: both consume the existing race-state dict and
  competitor list, and feed Granite explanations, so they can be replaced with a
  real mathematical engine without touching the AI layer. Recommended remediation:
  a pure-Python tire/fuel/pit/undercut model behind the existing
  `recommend_strategy` / `simulate_strategy` signatures.

## Result

All existing API contracts and response shapes preserved (additive fields only).
Existing tests still pass; coverage raised from 5 to 30 tests.
