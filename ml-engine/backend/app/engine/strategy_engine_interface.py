from app.schemas.strategy import StrategyRecommendation


def recommend_strategy(race_state, competitors):
    return StrategyRecommendation(
        recommended_action="PIT_NOW",
        confidence=0.84,
        risk_level="medium",
        reason_codes=[
            "HIGH_TIRE_DEGRADATION",
            "LOW_TRAFFIC_WINDOW"
        ]
    )