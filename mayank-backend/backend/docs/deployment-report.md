# Deployment Report

## Artifacts

| File | Purpose |
|------|---------|
| `Dockerfile` | Hardened: non-root user, `HEALTHCHECK` on `/health/`, cached dep layer, env-driven `$PORT` |
| `docker-compose.yml` | `backend` + optional `ollama` and `langflow` profiles |
| `.env.example` | All env vars documented; runs fully on defaults (echo provider) |
| `.dockerignore` | Excludes venv/tests/docs/secrets; **keeps** the Chroma index + `.env.example` |
| `railway.json` | Dockerfile build, `/health/` healthcheck, restart policy |
| `render.yaml` | Docker runtime web service, `/health/` healthcheck, secret env vars `sync:false` |
| `Procfile` | `web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` |

## Platform notes

- **Docker:** `docker compose up --build`. Add Granite/LangFlow via env or
  profiles: `docker compose --profile ollama up` (local Granite),
  `--profile langflow up` (orchestration server). When the `ollama` profile is
  up, the backend reaches it at `http://ollama:11434`.
- **Railway:** detects `railway.json`; injects `$PORT` (honored by the Dockerfile
  CMD). Set Granite/LangFlow vars in the dashboard.
- **Render:** `render.yaml` blueprint; secret vars are `sync:false` (set in
  dashboard). `/health/` used for health checks.

All three honor `$PORT`, so the same image runs everywhere. With no env set, the
service boots on the offline echo provider — a zero-config demo.

## Image size note

The image pulls `torch`/`transformers`/`chromadb`/`sentence-transformers` (multi-GB)
for the embedding model. This is inherent to the RAG stack. Options if size
matters: use a CPU-only torch wheel, or move embeddings to a hosted endpoint.

## Security (must-read before public deploy)

- **No authentication** on any endpoint and **CORS is fully open**
  (`allow_origins=["*"]`). Fine for a hackathon/demo; **not** for a public,
  multi-tenant deployment. First hardening step: add an API key / auth
  dependency and restrict CORS origins.
- Provider credentials are read from env only; none are committed. `.env` is
  git/Docker-ignored; only `.env.example` ships.

## Verification status (honest)

- **Validated here:** config files parse (`railway.json`, `render.yaml`,
  `docker-compose.yml`); app boots with all 20 routes; full test suite green
  offline; `uvicorn` start command matches across Dockerfile/Procfile/configs.
- **NOT run here:** a full `docker build` / `docker compose up`. The build pulls
  multi-GB ML wheels and takes many minutes, impractical inline. The Dockerfile
  is correct by inspection and mirrors the verified local run command. Recommend
  one `docker compose up --build` smoke test in CI before the first deploy.

## Quick start

```bash
cd backend
cp .env.example .env            # optional; defaults work offline
docker compose up --build       # http://localhost:8000  (/docs, /health/)
```
