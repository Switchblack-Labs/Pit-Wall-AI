from langchain_chroma import Chroma

from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_groq import ChatGroq

from app.rag.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    CHROMA_DB_DIR
)

from app.rag.prompts import RAG_PROMPT


embedding_function = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

vector_store = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embedding_function
)

retriever = vector_store.as_retriever()

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=LLM_MODEL
)


def ask(question):

    docs = retriever.invoke(question)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    final_prompt = RAG_PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(final_prompt)

    return response.content