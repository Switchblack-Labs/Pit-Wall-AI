import os


# Legacy Groq settings (no longer used for inference; kept so any external
# importer does not break). Inference now flows through app.llm.GraniteProvider.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHROMA_DB_DIR = "app/rag/chroma_db"

# Number of chunks to retrieve per query (tunable for grounding quality).
RETRIEVAL_K = int(os.getenv("RAG_RETRIEVAL_K", "4"))