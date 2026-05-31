# LangFlow Integration

LangFlow is an **optional** orchestration layer for Pit Wall AI. The backend
runs fully without it installed or reachable — the Python workflows in
`app/orchestration/` are the **source of truth**, and LangFlow is a pluggable
alternative execution path.

## Architecture

```
                         ┌─────────────────────────────┐
   /api/rag/query  ─────▶│ FiaWorkflow.run()           │
                         │   LANGFLOW_URL set?          │
                         │     yes → POST to LangFlow ──┼──▶ LangFlow server
                         │     (on failure ↓ fallback)  │     (fia_workflow)
                         │   in-process pipeline:       │
                         │     answer_question()  ──────┼──▶ Chroma + Granite
                         └─────────────────────────────┘

  /api/explain/  ──────▶  ExplainabilityWorkflow.run()  (same optional/fallback shape)
```

Both workflows try LangFlow first **only if** `LANGFLOW_URL` is configured, and
fall back to the in-process pipeline on any error. `run()` returns a `source`
field (`"langflow"` or `"in_process"`) so callers and tests can see which path
served the request.

## Workflows

| Workflow | Pipeline | Source of truth | Flow JSON |
|----------|----------|-----------------|-----------|
| **FIA** | Question → Retriever → Context Builder → Granite → Answer | `app/orchestration/fia_workflow.py` | `langflow/flows/fia_workflow.json` |
| **Explainability** | Recommendation → Reasoning → Granite → Explanation | `app/orchestration/explainability_workflow.py` | `langflow/flows/explainability_workflow.json` |

The exported flow JSON mirrors the Python pipeline node-for-node.

## Running without LangFlow (default)

Nothing to do. With `LANGFLOW_URL` unset, every workflow runs in-process. This
is the default for local dev, CI, and the hackathon demo.

## Running with LangFlow (optional)

1. Start a LangFlow server (e.g. `pip install langflow && langflow run`, or the
   `langflow` profile in `docker-compose.yml`).
2. Import the flows from `langflow/flows/` via the LangFlow UI (**Import**) or
   API. The `GraniteModel` / `ChromaSearch` nodes are descriptive placeholders;
   wire them to your LangFlow components and bind the same env vars the backend
   uses (`WATSONX_*` / `REPLICATE_API_TOKEN` / `OLLAMA_*`, and the Chroma
   `persist_directory`).
3. Point the backend at the server:

   ```bash
   export LANGFLOW_URL="http://localhost:7860"
   export LANGFLOW_API_KEY="..."   # if your server requires it
   ```

4. Restart the backend. Requests now execute via LangFlow, falling back
   in-process automatically if the server is unreachable.

The client calls `POST {LANGFLOW_URL}/api/v1/run/{flow_id}` where `flow_id` is
the flow's `endpoint_name` (`fia_workflow`, `explainability_workflow`). See
`app/orchestration/langflow_client.py`.

## Why services remain the source of truth

* **No hard dependency** — `langflow` is not imported by the backend; only
  `requests` (already a dependency) is used to reach a server.
* **Deterministic fallback** — a missing/broken LangFlow server never breaks an
  endpoint.
* **Testability** — the in-process pipelines are unit-testable offline with the
  `echo` provider.
