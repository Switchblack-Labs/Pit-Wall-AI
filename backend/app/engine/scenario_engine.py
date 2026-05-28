from app.schemas.simulation import SimulationResult


def simulate_strategy(
    scenario_type: str,
    laps_until_action: int
):
    if scenario_type == "pit_now":
        return SimulationResult(
            projected_position=3,
            projected_gap=2.1,
            projected_risk="low"
        )

    if scenario_type == "stay_out":
        return SimulationResult(
            projected_position=6,
            projected_gap=8.4,
            projected_risk="high"
        )

    return SimulationResult(
        projected_position=5,
        projected_gap=5.0,
        projected_risk="medium"
    )
