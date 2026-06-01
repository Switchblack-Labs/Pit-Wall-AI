from fastapi import APIRouter

from pydantic import BaseModel

from app.rag.rag_chain import ask


router = APIRouter(
    prefix="/api/rag",
    tags=["rag"]
)


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query_rag(payload: QueryRequest):

    response = ask(payload.question)

    return {
        "question": payload.question,
        "answer": response
    }