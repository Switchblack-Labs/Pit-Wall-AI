from pydantic import BaseModel


class AIExplanationResponse(BaseModel):
    explanation: str