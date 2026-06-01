"""
Projected race finish simulator.
Given current state and a decision, project where the driver finishes.
"""
import json
import os
import numpy as np
from ml_engine.math_engine.degradation import DegradationModel
from ml_engine.math_engine.overtake import OvertakeModel


class RaceProjector:
    def __init__(self, deg_model: DegradationModel, overtake_model: OvertakeModel):
        self.deg = deg_model
        self.overtake = overtake_model
        self.aggression_profiles = self._load_aggression()

    def _load_aggression(self):
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models", "saved", "aggression_profiles.json"
        )
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def project(self, state, decision, competitors=None):
        """
        Project race finish given a decision.

        state: dict with race state fields
        decision: "STAY_OUT", "PIT_SOFT", "PIT_MEDIUM", "PIT_HARD"
        competitors: list of dicts with other drivers' states

        Returns: {projected_position, projected_gap_to_leader, projected_lap_times, reasoning}
        """
        circuit = state.get("circuit") or "unknown"
        laps_remaining = state.get("laps_remaining") or 20
        current_position = state.get("position") or 10
        gap_to_leader = state.get("gap_to_leader_s") or 0
        pit_loss = state.get("pit_loss_s") or 22.0
        track_temp = state.get("track_temp")

        # Current tyre state
        compound = state.get("compound") or "MEDIUM"
        tyre_life = state.get("tyre_life") or 10

        # Apply decision
        if decision == "STAY_OUT":
            sim_compound = compound
            sim_tyre_life_start = tyre_life
            pit_lap = None
        else:
            # PIT_SOFT, PIT_MEDIUM, PIT_HARD
            new_compound = decision.replace("PIT_", "")
            sim_compound = new_compound
            sim_tyre_life_start = 0
            pit_lap = 0  # pit this lap
            gap_to_leader += pit_loss  # lose time in pit

        # Simulate lap by lap
        projected_times = []
        total_time = gap_to_leader
        current_tyre_life = sim_tyre_life_start

        for lap_offset in range(1, laps_remaining + 1):
            if pit_lap == 0 and lap_offset == 1:
                # Pit stop lap: add pit loss, reset tyres
                current_tyre_life = 1
            else:
                current_tyre_life += 1

            lap_time = self.deg.predict_lap_time(circuit, sim_compound, current_tyre_life, track_temp)
            if lap_time is None:
                lap_time = 90.0  # fallback

            projected_times.append(lap_time)
            total_time += lap_time

        # Project competitor finish times
        if competitors:
            projected_position = self._project_position(
                total_time, current_position, competitors,
                circuit, laps_remaining, track_temp
            )
        else:
            # Without competitor data, estimate position change from pace delta
            avg_pace = np.mean(projected_times) if projected_times else 90.0
            if decision == "STAY_OUT":
                # Staying out: position likely degrades as tyres wear
                deg_penalty = self.deg.predict_deg_rate(circuit, compound, tyre_life + laps_remaining // 2) * laps_remaining * 0.1
                projected_position = current_position + int(deg_penalty)
            else:
                # Pitting: lose position now, gain later
                positions_lost_in_pit = min(3, max(1, int(pit_loss / 5)))
                # But gain from fresh tyres
                fresh_advantage = self.deg.predict_deg_rate(circuit, compound, tyre_life) * laps_remaining * 0.3
                positions_gained = int(fresh_advantage)
                projected_position = current_position + positions_lost_in_pit - positions_gained

            projected_position = max(1, min(20, projected_position))

        return {
            "decision": decision,
            "projected_position": projected_position,
            "projected_total_time": float(total_time),
            "projected_lap_times": projected_times,
            "avg_projected_pace": float(np.mean(projected_times)) if projected_times else None,
        }

    def _project_position(self, my_total_time, my_position, competitors,
                           circuit, laps_remaining, track_temp):
        """Project position relative to competitors."""
        my_time = my_total_time
        ahead_count = 0

        for comp in competitors:
            comp_time = self._project_competitor_time(comp, circuit, laps_remaining, track_temp)
            if comp_time < my_time:
                ahead_count += 1

        return ahead_count + 1

    def _project_competitor_time(self, comp, circuit, laps_remaining, track_temp):
        """Project total race time for a competitor, adjusted for driver aggression."""
        total = comp.get("gap_to_leader_s") or 0
        compound = comp.get("compound") or "MEDIUM"
        tyre_life = comp.get("tyre_life") or 10

        # Aggression affects stint extension: aggressive drivers push harder
        # on worn tyres (slightly faster early, but more deg late)
        driver = comp.get("driver")
        aggr = 0.5
        if driver and driver in self.aggression_profiles:
            aggr = self.aggression_profiles[driver]["aggression"]

        # Aggressive drivers extract ~0.5-1.5% more from worn tyres early
        # but hit cliff harder. Net effect: stint_extension laps longer.
        stint_ext = int((aggr - 0.5) * 5)  # -2 to +2 laps vs neutral

        for lap in range(1, laps_remaining + 1):
            effective_tyre = tyre_life + lap - stint_ext
            effective_tyre = max(1, effective_tyre)
            t = self.deg.predict_lap_time(circuit, compound, effective_tyre, track_temp)
            if t is None:
                t = 90.0
            total += t

        return total

    def compare_decisions(self, state, competitors=None):
        """Compare all possible decisions and return ranked results."""
        decisions = ["STAY_OUT", "PIT_SOFT", "PIT_MEDIUM", "PIT_HARD"]
        results = []

        for decision in decisions:
            result = self.project(state, decision, competitors)
            results.append(result)

        # Sort by projected position (best first)
        results.sort(key=lambda x: (x["projected_position"], x["projected_total_time"]))
        return results
