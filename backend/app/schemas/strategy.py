from typing import List
from pydantic import BaseModel


class StrategyRecommendation(BaseModel):
    recommended_action: str
    confidence: float
    risk_level: str
    reason_codes: List[str]