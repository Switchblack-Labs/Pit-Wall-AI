from app.schemas.ai import AIExplanationResponse


class GraniteClient:
    async def explain_strategy(
        self,
        recommendation: str,
        confidence: float,
        risk: str,
        reasons: list[str]
    ) -> AIExplanationResponse:

        explanation = (
            f"{recommendation} recommended "
            f"with {confidence:.0%} confidence "
            f"due to {', '.join(reasons)}."
        )

        return AIExplanationResponse(
            explanation=explanation
        )