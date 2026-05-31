"""Prompt templates for Granite-powered strategy explanations.

Mirrors the structure of ``app/prompts/strategy_prompt.txt`` but is kept in
Python so the explanation service can format it directly.
"""

EXPLANATION_SYSTEM_PROMPT = (
    "You are an elite Formula 1 race engineer giving a pit-wall explanation to "
    "your driver and strategists.\n"
    "Explain the strategy recommendation clearly, concisely and with confidence.\n"
    "Ground every statement in the supplied recommendation, confidence, risk "
    "level and reason codes. Do not invent telemetry or rules.\n"
    "Keep it to 2-4 sentences, in plain race-engineer language."
)

EXPLANATION_USER_PROMPT = (
    "RECOMMENDED ACTION: {recommendation}\n"
    "CONFIDENCE: {confidence}\n"
    "RISK LEVEL: {risk}\n"
    "REASON CODES: {reasons}\n"
    "{context}\n"
    "Write the explanation now."
)


def build_explanation_prompt(
    *,
    recommendation: str,
    confidence: str,
    risk: str,
    reasons: str,
    context: str = "",
) -> str:
    """Format the explanation user-prompt from strategy fields."""
    context_block = f"ADDITIONAL CONTEXT:\n{context}\n" if context else ""
    return EXPLANATION_USER_PROMPT.format(
        recommendation=recommendation,
        confidence=confidence,
        risk=risk,
        reasons=reasons,
        context=context_block,
    )
