# Production Readiness Report

Final end-to-end audit of the Pit Wall AI backend after the Granite / RAG /
LangFlow / TORCS work. Every claim below was verified by running code, not by
inspection alone (exceptions are called out explicitly).

---

## 1. Production Readiness Score: **86 / 100**

| Category | Score | Notes |
|----------|-------|-------|
| Functionality & backward compat | 19/20 | 30/30 tests pass; all routes 200; OpenAPI loads; contracts additive-only |
| FIA RAG | 17/20 | Retrieval + citations + grounding verified; citations source-level (no page #s) |
| Granite abstraction | 18/20 | Selection/fallback fully verified offline; live cloud calls not exercised |
| LangFlow | 9/10 | JSON valid; enable/disable + fallback verified; no live server round-trip |
| TORCS | 9/10 | Sim + ingest + interfaces verified; HTTP-streaming covered at component level |
| Deployment | 8/10 | Configs consistent & valid; `docker build` not run inline |
| Security | 6/10 | Clean secret hygiene, **but no auth + open CORS** (by design) |

Deductions are concentrated in (a) the deliberately-out-of-scope hardcoded
strategy/sim engines, (b) no endpoint auth, and (c) live external integrations
(Granite cloud, LangFlow server, docker build) not exercised in this hermetic
environment.

---

## 2. Verification Results

### Functionality ✅
- `pytest`: **30 passed** (was 5), fully offline (`LLM_PROVIDER=echo`).
- App boots; `app.openapi()` builds (14 paths); `/docs`, `/openapi.json`,
  `/health/`, `/` all 200.
- All original endpoints intact; new fields on `/api/rag/query`
  (`citations`, `grounded`) are additive. **No broken contracts.**

### FIA RAG ✅
- ChromaDB loads from the persisted index; retrieval returns relevant chunks
  (k tunable, default 4).
- Citations resolve to FIA source PDFs with snippets; grounding guard returns a
  deterministic refusal with `grounded=false` when retrieval is empty.
- Generation flows through the provider abstraction (Granite-first).

### Granite ✅
- watsonx / replicate / ollama all correctly report `is_available()=False`
  without creds/SDK/server (no crashes, lazy SDK imports).
- Every `LLM_PROVIDER` value (`auto`/`watsonx`/`replicate`/`ollama`/`echo`/
  unknown) resolves to a working provider; unknown logs a warning and
  auto-selects. Custom `LLM_FALLBACK_ORDER` honored. Generation-error fallback
  verified by unit test.

### LangFlow ✅
- Both flow JSON files parse; `endpoint_name`s correct.
- Client disabled with no URL, enabled when `LANGFLOW_URL` set; workflows run
  in-process when disabled and fall back when a server returns nothing.

### TORCS ✅
- Simulated source produces bounds-valid frames (seeded/deterministic).
- Ingestor feeds telemetry + competitors + both WebSocket channels and updates
  shared race state; existing `/api/telemetry` flow unaffected.
- Both `SimulatedTorcsSource` and `LiveTorcsSource` conform to the `TorcsSource`
  interface (plug-and-play swap). Start/stop endpoints tested.

### Deployment ✅
- Startup command identical across Dockerfile / Procfile / railway.json
  (uvicorn + `$PORT`); render healthcheck `/health/`.
- `railway.json`, `render.yaml`, `docker-compose.yml` all parse. Chroma index is
  git-tracked so it ships in the image.

### Security ⚠️
- **No hardcoded secrets** in app code; all creds via `os.getenv`/Settings.
- `.env` is gitignored and untracked; only `.env.example` on disk.
- Logging is structured JSON and logs no secret values (provider names/levels
  only).
- ⚠️ **No authentication on any endpoint; CORS `allow_origins=["*"]`.** Matches
  original design; acceptable for hackathon/demo, must be addressed before a
  public multi-tenant deployment.

### Code Quality ✅
- Fixed during this audit: unused `Optional` import (`rag_chain.py`) and an
  unused `vector_store` assignment (`vector_store.py`).
- Removed earlier: empty duplicate granite client; duplicate `rag_router`
  import.
- Remaining pyflakes hits (2) are **intentional** `# noqa: F401` SDK-availability
  probes, not dead code.
- Lazy embedding/Chroma load avoids the obvious startup performance issue.

---

## 3. Remaining Risks

1. **No endpoint auth / open CORS** — highest risk for any non-demo deployment.
2. **Live Granite paths unproven** — watsonx/replicate response parsing is
   written to documented SDK shapes but not validated against a live call (no
   creds/SDKs here). Risk surfaces only when real creds are first used.
3. **Hardcoded strategy/simulation engines** — `/api/strategy/recommend` and
   `/api/simulate/` return fixed values regardless of input (out of scope, owned
   by another teammate). Explanations are real, but explain a stubbed decision.
4. **Image size** — torch/transformers pull multi-GB; first cold deploy is slow.
5. **In-memory state** — race state is process-local; no persistence/HA. Fine
   for a single-instance demo.

---

## 4. Remaining Technical Debt

- Two committed `.pyc` files under `app/utils/__pycache__/` predate `.gitignore`
  and are still tracked (cleanup queued; cosmetic).
- `langchain-groq` still installed in the venv though no longer imported.
- RAG citations are source-level (no article/page numbers) — would need
  re-ingestion with per-page metadata.
- `datetime.utcnow()` used (consistent with existing code) — deprecated in 3.12+;
  migrate to `datetime.now(UTC)` project-wide later.
- TORCS HTTP-streaming verified at component level only (TestClient WebSocket
  portal deadlocks on `create_task` — harness artifact, not a runtime bug).

---

## 5. Recommended Future Improvements

1. Add an auth dependency (API key/bearer) and restrict CORS origins.
2. Smoke-test each real Granite provider once with live creds; add a
   `/api/llm/health` endpoint reporting the active provider.
3. Replace the hardcoded strategy/sim engines with a real pure-Python
   tire/fuel/pit/undercut model behind the existing signatures.
4. Add `pytest-cov` to CI and a `docker compose up --build` smoke job.
5. Persist race state (Redis) for multi-instance deployments.
6. Page-level RAG citations via re-ingestion with per-page metadata.

---

## 6. Hackathon Submission: **READY ✅**

The backend runs end-to-end with zero configuration (offline echo provider),
all 30 tests pass, Swagger is live, and the headline features — Granite
abstraction, FIA RAG with citations, LangFlow orchestration, and TORCS simulated
telemetry — are functional and demoable. Real Granite is a credentials-only
switch with no code change.

## 7. Deployment: **READY for single-instance / demo ✅ — conditional for public ⚠️**

Deployable to Railway / Render / Docker today (configs validated, healthchecks
wired, `$PORT` honored). **Before a public, multi-tenant deployment**, address:
endpoint authentication, CORS restriction, and one live `docker compose up`
smoke test. None of these block a hackathon demo or an internal/single-tenant
deploy.

---

### Audit summary
Issues found: 4 (2 code-quality, both fixed; 1 security posture, flagged; 1 git
hygiene, queued). No test failures. No broken contracts. No exposed secrets.
