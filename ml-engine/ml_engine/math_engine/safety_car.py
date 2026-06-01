"""
Safety car and VSC pit decision logic.
"""


class SafetyCarAdvisor:
    # SC/VSC reduces pit loss by approximately this much
    SC_PIT_SAVING = 10.0  # seconds saved vs green flag pit
    VSC_PIT_SAVING = 8.0

    def __init__(self, deg_model, undercut_calc):
        self.deg_model = deg_model
        self.undercut = undercut_calc

    def advise(self, track_status, circuit, driver_state, competitors=None):
        """
        Decide whether to pit under SC/VSC.
        Returns dict with decision, confidence, reasoning.
        """
        is_sc = track_status in ("SafetyCar", "4")
        is_vsc = track_status in ("VSC", "6")

        if not is_sc and not is_vsc:
            return {"decision": "N/A", "confidence": 0, "reasoning": "No safety car"}

        pit_saving = self.SC_PIT_SAVING if is_sc else self.VSC_PIT_SAVING
        effective_pit_loss = driver_state.get("pit_loss_s", 22.0) - pit_saving

        tyre_life = driver_state.get("tyre_life") or 10
        compound = driver_state.get("compound") or "MEDIUM"
        laps_remaining = driver_state.get("laps_remaining") or 20
        position = driver_state.get("position") or 10
        gap_behind = driver_state.get("gap_behind_s")
        stops_made = driver_state.get("stops_made") or 1
        compounds_used = driver_state.get("compounds_used") or ""

        expected_stint = self.deg_model.expected_stint_length(circuit, compound)
        tyre_pct_used = tyre_life / max(expected_stint, 1)

        reasons = []
        score = 0  # positive = pit, negative = stay out

        # Factor 1: Tyre life
        if tyre_pct_used > 0.65:
            score += 3
            reasons.append(f"Tyres at {tyre_pct_used:.0%} of life - free pit stop")
        elif tyre_pct_used > 0.45:
            score += 1
            reasons.append(f"Tyres at {tyre_pct_used:.0%} - opportunistic stop")
        else:
            score -= 2
            reasons.append(f"Tyres at {tyre_pct_used:.0%} - too fresh to waste")

        # Factor 2: Position risk
        if position <= 3:
            # Leading positions: pitting under SC is risky if rivals don't
            if is_sc:
                score -= 1
                reasons.append("Leading position - SC pit risks losing track position")
            # But VSC is lower risk
        else:
            score += 1
            reasons.append("Mid/back position - less to lose from pitting")

        # Factor 3: Gap behind (will we lose position?)
        if gap_behind is not None:
            if gap_behind > effective_pit_loss:
                score += 2
                reasons.append(f"Gap behind ({gap_behind:.1f}s) > pit loss ({effective_pit_loss:.1f}s) - safe pit")
            elif gap_behind < effective_pit_loss * 0.5:
                score -= 1
                reasons.append(f"Gap behind ({gap_behind:.1f}s) too small - will lose position")

        # Factor 4: Laps remaining
        if laps_remaining < 10:
            if tyre_pct_used < 0.5:
                score -= 3
                reasons.append(f"Only {laps_remaining} laps left on fresh-ish tyres - no pit")
            else:
                score += 1
                reasons.append(f"{laps_remaining} laps left on worn tyres - grab the free stop")

        # Factor 5: Compound obligation
        used_set = set(compounds_used.split(",")) if compounds_used else set()
        used_set.discard("")
        if len(used_set) < 2 and stops_made == 0:
            score += 2
            reasons.append("Haven't fulfilled 2-compound rule yet - use the free stop")

        # Factor 6: Under SC, everyone bunches up - resets gaps
        if is_sc and position <= 3 and tyre_pct_used < 0.5:
            score -= 2
            reasons.append("SC bunches field - staying out on fresh tyres preserves track advantage")

        # Decision
        if score >= 2:
            decision = "PIT"
            confidence = min(0.95, 0.6 + score * 0.08)
        elif score <= -2:
            decision = "STAY_OUT"
            confidence = min(0.95, 0.6 + abs(score) * 0.08)
        else:
            decision = "PIT" if score > 0 else "STAY_OUT"
            confidence = 0.5 + abs(score) * 0.05

        # Recommend compound
        new_compound = self.undercut.best_pit_compound(
            circuit, laps_remaining, compounds_used
        )

        return {
            "decision": decision,
            "compound": new_compound,
            "confidence": round(confidence, 2),
            "reasoning": "; ".join(reasons),
            "score": score,
            "pit_saving_s": pit_saving,
            "effective_pit_loss_s": effective_pit_loss,
        }
