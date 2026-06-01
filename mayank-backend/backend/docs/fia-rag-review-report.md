# FIA RAG Review Report

## Pipeline (unchanged where it worked)

```
FIA PDFs ─▶ PyMuPDF (fitz) ─▶ RecursiveCharacterTextSplitter ─▶ MiniLM embeddings ─▶ ChromaDB (persisted) ─▶ similarity_search(k) ─▶ Granite ─▶ answer + citations
```

Per the "preserve working RAG" constraint, retrieval, embeddings, chunking and
ChromaDB were **not rewritten** — only incrementally improved.

## Documents

- `FIA 2026 F1 Regulations - Section B [Sporting] - Iss 06 - 2026-04-28.pdf`
- `fia_2026_f1_regulations_-_section_c_technical_-_iss_18_-_2026-05-07.pdf`

Indexed into `app/rag/chroma_db/` (~15 MB `chroma.sqlite3`), shipped in the image.

## Configuration

| Setting | Value | File |
|---------|-------|------|
| Chunk size / overlap | 1000 / 200 | `app/rag/ingest.py` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | `app/rag/config.py` |
| Retrieval k | `RAG_RETRIEVAL_K` (default 4) | `app/rag/config.py` |
| Generation | `GraniteProvider` (was Groq) | `app/rag/rag_chain.py` |

## Improvements made

1. **Granite inference** — answer generation now flows through the swappable
   provider instead of a hard-wired `ChatGroq`. Retrieval is untouched.
2. **Citations** — `answer_question()` returns `citations` (source PDF filename +
   a deduplicated text snippet) built from the retrieved chunks' `source`
   metadata. Exposed additively on `POST /api/rag/query`.
3. **Grounding / hallucination resistance** — two layers:
   - System prompt forbids outside knowledge and mandates a fixed refusal
     sentence when the context is insufficient.
   - A Python-level guard: if retrieval returns nothing, the chain returns the
     deterministic refusal with `grounded=false` and no citations. This is
     testable even offline (`tests/test_rag.py`).
4. **Lazy vector store** — embeddings + Chroma open on first query
   (`functools.lru_cache`), so importing the app / running unrelated tests does
   not load the model.
5. **Ingestion re-run guard** — `build_vector_store()` skips rebuilding when an
   index already exists (`force=True` to override).
6. **Tunable k** — retrieval breadth is now env-configurable.

## Honesty notes

- **Citations are source-level, not page-level.** `ingest.py` stores only the
  filename in chunk metadata; no page numbers are tracked, so citations name the
  regulation document + snippet, not an article/page. Adding page numbers would
  require re-ingesting with per-page metadata — deferred to avoid rebuilding the
  index (constraint: preserve working RAG).
- **Grounding guard is heuristic.** The strongest guarantee (empty retrieval →
  refusal) is deterministic; the in-context refusal depends on the model honoring
  the system prompt. With a real Granite model this is reliable; under the
  offline echo provider the answer text is non-substantive by design.

## Verification

`tests/test_rag.py` (offline): real retrieval returns ≥1 citation from a `.pdf`
source for an in-scope question; `ask()` still returns a `str`; forced empty
retrieval yields `grounded=false` + refusal text.
