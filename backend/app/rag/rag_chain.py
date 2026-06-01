"""FIA regulations RAG chain.

Retrieval, embeddings, chunking and ChromaDB are unchanged from the original,
working implementation. The only substantive change is that answer generation
now flows through the swappable :class:`~app.llm.base.GraniteProvider`
(Granite-first, with automatic offline fallback) instead of a hard-wired Groq
client, and the chain now returns grounding citations plus a hallucination
guard.

Backward compatibility:
* ``ask(question) -> str`` keeps its original signature and return type.
* ``RAG_PROMPT`` is still honoured for any external caller.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, TypedDict

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.llm.factory import get_llm_provider
from app.rag.config import CHROMA_DB_DIR, EMBEDDING_MODEL, RETRIEVAL_K
from app.rag.prompts import (
    NOT_IN_REGULATIONS,
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT,
)
from app.utils.logger import logger


class Citation(TypedDict):
    source: str
    snippet: str


class RagAnswer(TypedDict):
    answer: str
    citations: List[Citation]
    grounded: bool


@lru_cache(maxsize=1)
def _get_embeddings() -> HuggingFaceEmbeddings:
    """Lazily build the embedding function (loads the model once)."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _get_vector_store() -> Chroma:
    """Lazily open the persisted Chroma index (built by ``vector_store.py``)."""
    return Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=_get_embeddings(),
    )


def _retrieve(question: str, k: int = RETRIEVAL_K):
    """Return up to ``k`` relevant chunks for ``question``.

    Uses similarity search directly so we keep the documents (and their
    ``source`` metadata) for citation building.
    """
    store = _get_vector_store()
    try:
        return store.similarity_search(question, k=k)
    except Exception as exc:
        logger.error("RAG retrieval failed: %s", exc)
        return []


def _build_context(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _build_citations(docs, snippet_len: int = 240) -> List[Citation]:
    citations: List[Citation] = []
    seen = set()
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        snippet = " ".join(doc.page_content.split())[:snippet_len]
        key = (source, snippet[:60])
        if key in seen:
            continue
        seen.add(key)
        citations.append({"source": source, "snippet": snippet})
    return citations


def answer_question(question: str, *, k: int = RETRIEVAL_K) -> RagAnswer:
    """Full RAG answer with citations and a grounding flag.

    The grounding guard works at two levels:
    1. If retrieval returns nothing, we refuse deterministically (so the guard
       is testable even with the offline echo provider).
    2. The system prompt instructs the model to emit ``NOT_IN_REGULATIONS``
       when the context is insufficient.
    """
    docs = _retrieve(question, k=k)

    if not docs:
        return {"answer": NOT_IN_REGULATIONS, "citations": [], "grounded": False}

    context = _build_context(docs)
    citations = _build_citations(docs)

    provider = get_llm_provider()
    user_prompt = RAG_USER_PROMPT.format(context=context, question=question)
    result = provider.generate(
        user_prompt,
        system=RAG_SYSTEM_PROMPT,
        max_tokens=512,
        temperature=0.1,
    )

    answer = (result.text or "").strip()
    grounded = NOT_IN_REGULATIONS.lower() not in answer.lower() and bool(answer)

    return {
        "answer": answer,
        "citations": citations if grounded else [],
        "grounded": grounded,
    }


def ask(question: str) -> str:
    """Backward-compatible entry point returning just the answer text."""
    return answer_question(question)["answer"]
