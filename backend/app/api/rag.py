from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.orchestration.fia_workflow import FiaWorkflow


router = APIRouter(
    prefix="/api/rag",
    tags=["rag"]
)

# Source-of-truth orchestration pipeline (uses LangFlow if configured, else
# runs the in-process RAG chain). Constructed once; cheap and stateless.
_fia_workflow = FiaWorkflow()


class QueryRequest(BaseModel):
    question: str


class CitationModel(BaseModel):
    source: str
    snippet: str


class RagResponse(BaseModel):
    # Existing fields preserved for backward compatibility.
    question: str
    answer: str
    # Additive fields (Optional-with-defaults so existing clients are unaffected).
    citations: List[CitationModel] = []
    grounded: bool = True


@router.post("/query", response_model=RagResponse)
def query_rag(payload: QueryRequest) -> RagResponse:
    result = _fia_workflow.run(payload.question)

    return RagResponse(
        question=payload.question,
        answer=result["answer"],
        citations=[CitationModel(**c) for c in result["citations"]],
        grounded=result["grounded"],
    )
