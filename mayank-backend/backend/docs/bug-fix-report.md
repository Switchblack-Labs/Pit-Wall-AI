# Bug Fix Report

Bugs and defects found and fixed during this work. Each was verified.

## 1. Duplicate `rag_router` import in `main.py`
- **Was:** `from app.api.rag import router as rag_router` appeared twice (the
  second, after `include_router` calls, was dead and confusing).
- **Fix:** removed the duplicate during the `lifespan` migration.

## 2. Deprecated FastAPI startup/shutdown events
- **Was:** `@app.on_event("startup"/"shutdown")` — deprecated, emits warnings,
  and left no clean shutdown for background tasks.
- **Fix:** migrated to an `asynccontextmanager` `lifespan` that also stops any
  running TORCS stream on shutdown.

## 3. Empty/duplicate "Granite" client
- **Was:** `app/integrations/granite_client.py` was 0 bytes (dead duplicate of
  `app/clients/granite_client.py`).
- **Fix:** removed it; the real client is now a Granite-provider adapter.

## 4. Missing runtime dependencies
- **Was:** `app/rag/ingest.py` imports `fitz` (**PyMuPDF**) and
  `langchain_text_splitters`, but neither was in `requirements.txt`; `docling`
  was listed but unused for parsing. A clean install would fail to ingest.
- **Fix:** added `PyMuPDF` and `langchain-text-splitters`; pinned all
  `langchain*`/`chromadb`/`sentence-transformers`/`transformers` to installed
  versions; moved `docling`/`replicate` to optional.

## 5. Negative competitor tire wear in TORCS simulator (found via test)
- **Was:** `min(1.0, tire_wear + uniform(-0.1, 0.2))` clamped only the upper
  bound, so `tire_wear` could be negative and fail `TorcsCompetitorGap`
  (`ge=0`) validation — a hard crash mid-stream.
- **Fix:** two-sided clamp `min(1.0, max(0.0, ...))`. Regression assertion added.

## 6. `/api/explain/` could fail / return unhelpful text
- **Was:** the explanation depended on a fake client and had no resilience path;
  any future real-model error would surface as a 500.
- **Fix:** real Granite call wrapped with a deterministic template fallback and
  exception handling so the endpoint always returns 200 with sensible text.

## 7. Deprecated Pydantic settings config
- **Was:** inner `class Config` on `Settings` (Pydantic v2 deprecation warning).
- **Fix:** `model_config = SettingsConfigDict(...)`; also added `extra="ignore"`
  so unknown env vars don't crash startup.

## 8. Eager embedding-model load on import
- **Was:** `rag_chain.py` built `HuggingFaceEmbeddings` + `Chroma` at module
  import, loading the model even for unrelated requests/tests.
- **Fix:** lazy `lru_cache` accessors; the model loads on first query only.

## Verified not-a-bug

- `WebSocketService.broadcast` already removes dead connections on send failure.
- The websocket endpoint already handles `WebSocketDisconnect`.
- `app/api/ai.py` is an empty, unregistered stub — harmless; left as-is.
