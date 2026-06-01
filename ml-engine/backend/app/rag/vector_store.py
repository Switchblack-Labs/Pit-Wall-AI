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


def build_vector_store():

    documents = load_documents()

    chunks = create_chunks(documents)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=CHROMA_DB_DIR
    )

    print(f"{len(chunks)} chunks stored in vector DB")


if __name__ == "__main__":

    build_vector_store()