import os


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHROMA_DB_DIR = "app/rag/chroma_db"