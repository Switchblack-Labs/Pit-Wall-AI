"""
Main strategy engine. Combines math engine + ML models into a single
importable class that the backend can call.

Usage:
    engine = StrategyEngine()
    engine.load_models()
    result = engine.recommend(race_state_dict)
"""
import os
from ml_engine.math_engine.degradation import DegradationModel
from ml_engine.math_engine.undercut import UndercutCalculator
from ml_engine.math_engine.safety_car import SafetyCarAdvisor
from ml_engine.math_engine.overtake import OvertakeModel
from ml_engine.math_engine.projection import RaceProjector
from ml_engine.models.deg_predictor import DegPredictor
from ml_engine.models.overtake_model import OvertakePredictor
from ml_engine.config import MODEL_DIR


class StrategyEngine:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or MODEL_DIR
        self.deg_model = DegradationModel()
        self.overtake_model = OvertakeModel()
        self.undercut_calc = UndercutCalculator(self.deg_model)
        self.sc_advisor = SafetyCarAdvisor(self.deg_model, self.undercut_calc)
        self.projector = RaceProjector(self.deg_model, self.overtake_model)

        self.deg_predictor = None  # ML model, loaded if available
        self.overtake_predictor = None

    def load_models(self):
        """Load all saved models."""
        curves_path = os.path.join(self.model_dir, "deg_curves.json")
        if os.path.exists(curves_path):
            self.deg_model.load(curves_path)

        # Load ML deg predictor if it beat baseline
        deg_pkl = os.path.join(self.model_dir, "deg_predictor.pkl")
        if os.path.exists(deg_pkl):
            self.deg_predictor = DegPredictor()
            self.deg_predictor.load()
            if self.deg_predictor.beats_baseline:
                print("Using ML deg predictor (beats scipy baseline)")

        # Load ML overtake model if it beat baseline
        ot_pkl = os.path.join(self.model_dir, "overtake_model.pkl")
        if os.path.exists(ot_pkl):
            self.overtake_predictor = OvertakePredictor()
            self.overtake_predictor.load()
            if self.overtake_predictor.beats_baseline:
                self.overtake_model.set_ml_model(self.overtake_predictor.model)
                print("Using ML overtake model (beats hardcoded rates)")

    def _best_sc_compound(self, circuit, laps_remaining, current_compound,
                           compounds_used, track_temp):
        """Find best compound for SC/VSC pit, considering all options."""
        used_set = set(compounds_used.split(",")) if compounds_used else set()
        used_set.discard("")
        two_compound_met = len(used_set) >= 2

        candidates = ["SOFT", "MEDIUM", "HARD"]
        best = None
        best_time = float("inf")

        for comp in candidates:
            if comp == current_compound:
                continue  # no point pitting for same compound

            stint_len = self.deg_model.expected_stint_length(circuit, comp)
            # If this compound won't last, skip (unless it's soft for a sprint)
            if comp == "HARD" and laps_remaining < 10:
                continue  # hard too slow for short sprint

            # If 2-compound rule not met and this is already used, less ideal
            # but still consider it
            total_time = 0
            laps_on_this = min(laps_remaining, stint_len)
            for lap in range(1, laps_on_this + 1):
                t = self.deg_model.predict_lap_time(circuit, comp, lap, track_temp)
                total_time += t if t else 90.0

            # Add penalty for another pit if won't last
            if stint_len < laps_remaining:
                total_time += 22.0

            if total_time < best_time:
                best_time = total_time
                best = comp

        return best

    def recommend(self, state, competitors=None):
        """
        Main entry point. Takes a race state dict and returns a strategy recommendation.
        """
        circuit = state.get("circuit") or "unknown"
        track_status = str(state.get("track_status") or "1")
        compound = state.get("compound") or "MEDIUM"
        tyre_life = state.get("tyre_life") or 10
        laps_remaining = state.get("laps_remaining") or 20
        gap_ahead = state.get("gap_ahead_s")
        gap_behind = state.get("gap_behind_s")
        pit_loss = state.get("pit_loss_s") or 22.0
        track_temp = state.get("track_temp")
        position = state.get("position") or 10
        compounds_used = state.get("compounds_used") or ""
        stops_made = state.get("stops_made") or 0

        analysis = {}
        reason_codes = []
        reasoning_parts = []

        # Use ACTUAL deg_rate from race data if available (more accurate than model prediction)
        actual_deg_rate = state.get("deg_rate")
        model_deg_rate = self.deg_model.predict_deg_rate(circuit, compound, tyre_life, track_temp)
        # Prefer actual race data, fall back to model
        deg_rate = actual_deg_rate if actual_deg_rate is not None else model_deg_rate
        analysis["deg_rate"] = deg_rate
        analysis["model_deg_rate"] = model_deg_rate

        # ML deg prediction if available
        if self.deg_predictor and self.deg_predictor.beats_baseline:
            ml_deg = self.deg_predictor.predict(
                circuit, compound, tyre_life, track_temp,
                laps_remaining=laps_remaining, total_laps=state.get("total_laps") or 57
            )
            if ml_deg is not None:
                analysis["ml_deg_delta"] = ml_deg

        # Projected tyre life remaining
        proj_tyre_laps = self.deg_model.expected_stint_length(circuit, compound) - tyre_life
        proj_tyre_laps = max(0, proj_tyre_laps)
        analysis["projected_tyre_laps"] = proj_tyre_laps

        # CRITICAL: If actual deg rate is extreme, override projected tyre laps
        if deg_rate and deg_rate > 0.2:
            # At >0.2s/lap, tyres are dying. Estimate laps to cliff from current rate
            cliff_threshold = 2.5  # seconds total loss acceptable
            laps_to_cliff = max(1, int(cliff_threshold / deg_rate))
            proj_tyre_laps = min(proj_tyre_laps, laps_to_cliff)
            analysis["projected_tyre_laps"] = proj_tyre_laps

        if proj_tyre_laps <= 3:
            reason_codes.append("CRITICAL_TYRE_WEAR")
            reasoning_parts.append(f"Tyres near cliff - only ~{proj_tyre_laps} laps remaining on {compound}")

        if deg_rate and deg_rate > 0.2:
            reason_codes.append("EXTREME_DEGRADATION")
            reasoning_parts.append(f"Extreme deg rate {deg_rate:.2f}s/lap - losing >0.2s every lap")
        elif deg_rate and deg_rate > 0.12:
            reason_codes.append("HIGH_DEGRADATION")
            reasoning_parts.append(f"High deg rate of {deg_rate:.2f}s/lap")
        elif deg_rate and deg_rate > 0.07:
            reason_codes.append("MODERATE_DEGRADATION")

        # FORCED PIT: If deg rate is high AND enough laps remaining for fresh tyres to pay off
        force_pit = False
        if deg_rate and laps_remaining > 8:
            # Calculate: total time loss from staying out vs pit cost
            total_deg_loss = deg_rate * laps_remaining  # seconds lost from deg over remaining race
            if deg_rate > 0.2 and proj_tyre_laps <= 10:
                force_pit = True  # extreme deg, near cliff
            elif deg_rate > 0.15 and total_deg_loss > pit_loss * 0.8:
                # High deg AND total projected loss approaches pit stop cost
                force_pit = True

        # 2. Safety car check
        is_sc = track_status in ("4", "SafetyCar", "6", "VSC")
        if is_sc:
            sc_advice = self.sc_advisor.advise(track_status, circuit, state, competitors)
            analysis["safety_car_advice"] = sc_advice

            # OVERRIDE SC advisor: if laps remaining is long, consider compound switch
            sc_laps_remaining = laps_remaining
            if sc_laps_remaining > 15:
                # Find the fastest compound for remaining distance
                # Don't restrict to unused - 2-compound rule may already be met
                best_sc_compound = self._best_sc_compound(
                    circuit, laps_remaining, compound, compounds_used, track_temp
                )
                if best_sc_compound and best_sc_compound != compound:
                    sc_advice["decision"] = "PIT"
                    sc_advice["compound"] = best_sc_compound
                    sc_advice["confidence"] = max(sc_advice["confidence"], 0.8)
                    sc_advice["reasoning"] += (
                        f"; OVERRIDE: {sc_laps_remaining} laps remaining, "
                        f"switch to {best_sc_compound} for pace advantage"
                    )

            if sc_advice["decision"] == "PIT":
                return {
                    "recommended_action": f"PIT_{sc_advice.get('compound', 'MEDIUM')}",
                    "confidence": sc_advice["confidence"],
                    "risk_level": "low",
                    "reason_codes": ["SAFETY_CAR_PIT_WINDOW"] + reason_codes,
                    "reasoning": f"Safety car: {sc_advice['reasoning']}",
                    "projections": {},
                    "analysis": analysis,
                }
            elif sc_advice["decision"] == "STAY_OUT":
                return {
                    "recommended_action": "STAY_OUT",
                    "confidence": sc_advice["confidence"],
                    "risk_level": "medium",
                    "reason_codes": ["SAFETY_CAR_STAY_OUT"] + reason_codes,
                    "reasoning": f"Safety car: {sc_advice['reasoning']}",
                    "projections": {},
                    "analysis": analysis,
                }

        # 3. Undercut/overcut analysis
        ahead_compound = compound
        ahead_tyre_life = tyre_life
        if competitors:
            ahead = [c for c in competitors if c.get("position") == position - 1]
            if ahead:
                ahead_compound = ahead[0].get("compound") or compound
                ahead_tyre_life = ahead[0].get("tyre_life") or tyre_life

        best_compound = self.undercut_calc.best_pit_compound(
            circuit, laps_remaining, compounds_used, track_temp=track_temp
        )

        undercut_viable, uc_laps, uc_gain = self.undercut_calc.undercut_viable(
            circuit, gap_ahead, pit_loss,
            compound, tyre_life, ahead_compound, ahead_tyre_life,
            best_compound or "MEDIUM", laps_remaining, track_temp
        )
        analysis["undercut_viable"] = undercut_viable

        behind_compound = compound
        if competitors:
            behind = [c for c in competitors if c.get("position") == position + 1]
            if behind:
                behind_compound = behind[0].get("compound") or compound

        overcut_viable, oc_margin = self.undercut_calc.overcut_viable(
            circuit, gap_behind, pit_loss,
            compound, tyre_life, behind_compound, best_compound or "MEDIUM",
            laps_remaining, track_temp
        )
        analysis["overcut_viable"] = overcut_viable

        if undercut_viable:
            reason_codes.append("UNDERCUT_VIABLE")
            reasoning_parts.append(f"Undercut possible in ~{uc_laps:.0f} laps, projected gain {uc_gain:.1f}s")

        # 4. Project outcomes for each decision
        projections = {}
        decisions_to_eval = ["STAY_OUT"]
        if best_compound:
            decisions_to_eval.append(f"PIT_{best_compound}")
        for comp in ["SOFT", "MEDIUM", "HARD"]:
            d = f"PIT_{comp}"
            if d not in decisions_to_eval:
                decisions_to_eval.append(d)

        for decision in decisions_to_eval:
            proj = self.projector.project(state, decision, competitors)
            projections[decision] = {
                "projected_position": proj["projected_position"],
                "projected_total_time": proj["projected_total_time"],
                "avg_pace": proj["avg_projected_pace"],
            }

        # 5. Make decision
        best_decision = min(projections, key=lambda d: (
            projections[d]["projected_position"],
            projections[d]["projected_total_time"]
        ))

        best_proj = projections[best_decision]
        stay_proj = projections.get("STAY_OUT", best_proj)

        # Force pit override for extreme degradation
        if force_pit and best_decision == "STAY_OUT":
            # Override: extreme deg means staying out is losing massive time
            pit_options = {k: v for k, v in projections.items() if k.startswith("PIT")}
            if pit_options:
                best_decision = min(pit_options, key=lambda d: (
                    pit_options[d]["projected_position"],
                    pit_options[d]["projected_total_time"]
                ))
                best_proj = projections[best_decision]
                reasoning_parts.append(
                    f"FORCED PIT: {deg_rate:.2f}s/lap deg is unsustainable, "
                    f"losing {deg_rate * laps_remaining:.1f}s total if staying out"
                )

        # Confidence based on position delta and deg severity
        pos_gain = stay_proj["projected_position"] - best_proj["projected_position"]
        if best_decision == "STAY_OUT":
            if deg_rate and deg_rate > 0.15:
                # High deg but still recommending stay out — low confidence
                confidence = 0.5
                reasoning_parts.append("Staying out despite elevated degradation")
            elif proj_tyre_laps > 10 and (deg_rate is None or deg_rate < 0.08):
                confidence = 0.85
                reasoning_parts.append("Good tyre life remaining, no need to pit")
            elif proj_tyre_laps <= 5:
                confidence = 0.5
                reasoning_parts.append("Tyres wearing but no better option available")
            else:
                confidence = 0.7
        else:
            confidence = 0.6 + min(0.3, pos_gain * 0.1)
            if force_pit:
                confidence = max(confidence, 0.85)
            if deg_rate and deg_rate > 0.15:
                confidence = max(confidence, 0.80)
            reasoning_parts.append(
                f"Pit for {best_decision.replace('PIT_', '')} projects P{best_proj['projected_position']} "
                f"vs P{stay_proj['projected_position']} staying out"
            )

        # Risk level
        if best_decision == "STAY_OUT" and proj_tyre_laps <= 5:
            risk_level = "high"
        elif pos_gain < 0:
            risk_level = "high"
        elif pos_gain == 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Laps remaining sanity: don't pit in last 5 laps unless critical
        if laps_remaining <= 5 and best_decision != "STAY_OUT":
            if proj_tyre_laps > 3 and (deg_rate is None or deg_rate < 0.2):
                best_decision = "STAY_OUT"
                confidence = 0.75
                reasoning_parts.append("Too few laps remaining to benefit from pit stop")
                reason_codes.append("LATE_RACE_STAY_OUT")

        return {
            "recommended_action": best_decision,
            "confidence": round(confidence, 2),
            "risk_level": risk_level,
            "reason_codes": reason_codes,
            "reasoning": ". ".join(reasoning_parts) if reasoning_parts else "Maintaining current strategy",
            "projections": projections,
            "analysis": analysis,
        }
