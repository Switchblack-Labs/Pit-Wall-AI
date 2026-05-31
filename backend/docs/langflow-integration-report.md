# LangFlow Integration Report

> Usage guide: [`langflow-integration.md`](./langflow-integration.md). This
> report summarizes what was built, the design decision, and verification.

## Decision

LangFlow is a **first-class but optional** orchestration layer. The Python
workflows in `app/orchestration/` are the **source of truth**; LangFlow is an
alternative execution path. The backend has **no hard dependency** on LangFlow —
`langflow` is never imported; only `requests` (already a dep) is used to reach a
running server.

## Delivered

| Artifact | Purpose |
|----------|---------|
| `app/orchestration/fia_workflow.py` | Question → Retriever → Context → Granite → Answer (reuses `answer_question`) |
| `app/orchestration/explainability_workflow.py` | Recommendation → Reasoning → Granite → Explanation (reuses `GraniteClient`) |
| `app/orchestration/langflow_client.py` | Optional client; `is_enabled()` only when `LANGFLOW_URL` set; `run_flow()` returns `None` on failure |
| `langflow/flows/fia_workflow.json` | Importable LangFlow graph, mirrors the Python pipeline |
| `langflow/flows/explainability_workflow.json` | Importable LangFlow graph |

Endpoints wired to workflows: `/api/rag/query` → `FiaWorkflow`,
`/api/explain/` → `ExplainabilityWorkflow`.

## Fallback behaviour

Each workflow tries LangFlow **only if** `LANGFLOW_URL` is configured, and falls
back to the in-process pipeline on any error or empty result. `run()` returns a
`source` field (`"langflow"` | `"in_process"`) for observability.

## Verification (`tests/test_orchestration.py`)

- Client disabled when no URL; `run_flow` short-circuits to `None`.
- FIA + Explainability run in-process when LangFlow off.
- FIA uses LangFlow when a fake client returns a result (`source="langflow"`).
- FIA falls back in-process when the fake client returns nothing.

All offline, via the echo provider.

## Limitations

- The exported flow JSON uses descriptive placeholder node types
  (`GraniteModel`, `ChromaSearch`); on import you bind them to real LangFlow
  components. They are not auto-runnable without that wiring — by design, since
  the Python pipelines are the runtime source of truth.
- A live LangFlow round-trip was not exercised here (no server running); the
  client + fallback paths are covered by tests with a fake client.
