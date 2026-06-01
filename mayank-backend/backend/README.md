# Pit Wall AI — Backend

AI-powered Formula 1 race-engineer assistant. FastAPI backend providing
telemetry ingestion, competitor tracking, strategy & simulation endpoints,
FIA-regulations RAG, explainable AI, real-time WebSocket streaming, optional
LangFlow orchestration, and a TORCS telemetry source.

## Quick start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Runs fully offline on the deterministic "echo" LLM provider — no keys needed.
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health/

### Docker

```bash
cp .env.example .env          # optional; defaults work offline
docker compose up --build     # http://localhost:8000
```

Optional profiles: `docker compose --profile ollama up` (local Granite),
`docker compose --profile langflow up` (orchestration server).

## Configuration

All configuration is environment-based; see [`.env.example`](./.env.example).
With nothing set, the backend runs on the offline `echo` provider. To use real
IBM Granite, set credentials and (optionally) `LLM_PROVIDER`:

| Provider | Env vars | `LLM_PROVIDER` |
|----------|----------|----------------|
| IBM watsonx.ai | `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` | `watsonx` |
| Replicate | `REPLICATE_API_TOKEN` | `replicate` |
| Ollama (local) | `OLLAMA_BASE_URL` | `ollama` |
| Offline echo | — | `echo` |
| Auto-select (default) | first available, ordered | `auto` |

`LLM_PROVIDER=auto` picks the first provider with valid credentials, falling
back to `echo`. See [`docs/granite-migration-report.md`](./docs/granite-migration-report.md).

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health/` | Health check |
| GET | `/` | Service banner |
| POST | `/api/telemetry/` | Ingest a telemetry frame |
| POST | `/api/competitors/` | Upsert a competitor |
| GET | `/api/competitors/` | List competitors |
| POST | `/api/strategy/recommend` | Strategy recommendation (uses current state) |
| POST | `/api/simulate/` | Run a scenario simulation |
| POST | `/api/explain/` | Granite explanation of the latest strategy |
| POST | `/api/rag/query` | Ask the FIA regulations RAG (answer + citations) |
| POST | `/api/demo/start` · `/stop` | Start/stop mock telemetry demo |
| POST | `/api/torcs/start` · `/stop` | Start/stop TORCS telemetry source |
| GET | `/api/mock/telemetry` | One mock telemetry frame |
| WS | `/ws/live` | Real-time broadcast stream |
| GET | `/debug/state` | Current race-state snapshot |

Full request/response schemas are in the live OpenAPI docs (`/docs`). Frontend
integration details are in [`docs/frontend-integration.md`](./docs/frontend-integration.md).

## Architecture

```
api/        FastAPI routers (thin)
services/   business logic (singletons, DI in app/dependencies.py)
state/      in-memory race/competitor/session state
llm/        Granite provider abstraction (watsonx | replicate | ollama | echo)
rag/        FIA RAG: PyMuPDF -> chunk -> MiniLM -> ChromaDB -> Granite
orchestration/  Python workflows (source of truth) + optional LangFlow client
integrations/torcs/  TORCS protocol, sources (sim + live), ingestion
engine/     strategy & simulation engines  (see "Known limitations")
```

## Subsystem docs

- [Backend review](./docs/backend-review-report.md)
- [FIA RAG](./docs/fia-rag-review-report.md)
- [Granite migration](./docs/granite-migration-report.md)
- [LangFlow integration](./docs/langflow-integration.md) · [report](./docs/langflow-integration-report.md)
- [TORCS integration](./docs/torcs-integration.md) · [report](./docs/torcs-integration-report.md)
- [Deployment](./docs/deployment-report.md)
- [Test coverage](./docs/test-coverage-report.md)
- [Production readiness](./docs/production-readiness-report.md)

## Testing

```bash
LLM_PROVIDER=echo python -m pytest tests/ -q   # 30 passed, offline
```

## Known limitations

- **Strategy & simulation engines** (`app/engine/`) currently return fixed
  values regardless of input — owned by another team member. Explanations are
  real Granite output but explain a stubbed decision. Integration points are
  stable. See [`docs/backend-review-report.md`](./docs/backend-review-report.md).
- **No authentication** and CORS is fully open — acceptable for the hackathon
  demo; address before any public deployment.
