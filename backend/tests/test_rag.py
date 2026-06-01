"""Tests for the FIA RAG chain (offline via echo provider).

These exercise the real ChromaDB index and embeddings, so they confirm
retrieval + citation building + the grounding guard end-to-end.
"""

from app.rag.rag_chain import answer_question, ask


def test_answer_question_returns_citations_and_grounded_flag():
    result = answer_question("What is the pit lane speed limit?")
    assert set(result.keys()) == {"answer", "citations", "grounded"}
    assert isinstance(result["answer"], str) and result["answer"]
    assert result["grounded"] is True
    assert len(result["citations"]) >= 1
    cite = result["citations"][0]
    assert "source" in cite and "snippet" in cite
    assert cite["source"].lower().endswith(".pdf")


def test_ask_is_backward_compatible_string():
    out = ask("What is DRS?")
    assert isinstance(out, str)


def test_grounding_guard_when_no_documents(monkeypatch):
    import app.rag.rag_chain as chain

    monkeypatch.setattr(chain, "_retrieve", lambda q, k=4: [])
    result = chain.answer_question("Who won the 1998 championship?")
    assert result["grounded"] is False
    assert result["citations"] == []
    assert "could not find" in result["answer"].lower()
