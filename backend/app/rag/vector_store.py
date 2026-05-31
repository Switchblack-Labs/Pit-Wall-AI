from pathlib import Path

from langchain_chroma import Chroma

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.rag.config import (
    EMBEDDING_MODEL,
    CHROMA_DB_DIR
)

from app.rag.ingest import (
    load_documents,
    create_chunks
)


embedding_function = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


def _index_exists() -> bool:
    """True if a persisted Chroma index is already present."""
    return Path(CHROMA_DB_DIR, "chroma.sqlite3").exists()


def build_vector_store(force: bool = False):

    if _index_exists() and not force:
        print(
            f"Chroma index already present at {CHROMA_DB_DIR}; skipping ingestion. "
            "Pass force=True to rebuild."
        )
        return

    documents = load_documents()

    chunks = create_chunks(documents)

    # from_documents persists to CHROMA_DB_DIR as a side effect.
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=CHROMA_DB_DIR
    )

    print(f"{len(chunks)} chunks stored in vector DB")


if __name__ == "__main__":

    build_vector_store()