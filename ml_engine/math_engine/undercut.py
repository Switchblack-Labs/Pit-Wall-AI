"""
Undercut and overcut viability calculations.
"""
from ml_engine.math_engine.degradation import DegradationModel


class UndercutCalculator:
    def __init__(self, deg_model: DegradationModel):
        self.deg_model = deg_model

    def undercut_viable(self, circuit, gap_ahead_s, pit_loss_s,
                        my_compound, my_tyre_life,
                        their_compound, their_tyre_life,
                        new_compound, laps_remaining, track_temp=None):
        """
        Check if undercut is viable.
        Returns (viable: bool, laps_to_close: float, projected_gain_s: float)
        """
        if gap_ahead_s is None or gap_ahead_s <= 0:
            return False, None, None

        # After pitting: I'm on fresh tyres, they're on old tyres
        my_fresh_pace = self.deg_model.predict_lap_time(circuit, new_compound, 1, track_temp)
        their_current_pace = self.deg_model.predict_lap_time(circuit, their_compound, their_tyre_life, track_temp)

        if my_fresh_pace is None or their_current_pace is None:
            return False, None, None

        # Pace advantage per lap on fresh vs their worn tyres
        pace_adv_per_lap = their_current_pace - my_fresh_pace
        if pace_adv_per_lap <= 0:
            return False, None, None

        # After pit, I rejoin gap_ahead + pit_loss behind them (approx)
        # But the "undercut effect": I come out on faster tyres
        # Key: do I emerge ahead after pit?
        gap_after_pit = gap_ahead_s  # simplified: they don't pit yet
        # In-lap advantage: my last lap before pit is slow, but out-lap on fresh is fast
        # Net: undercut works if fresh tyre advantage > gap_ahead within 2-3 laps

        laps_to_close = gap_after_pit / pace_adv_per_lap if pace_adv_per_lap > 0 else 999

        # Account for degradation of their pace over those laps
        cumulative_gain = 0
        for lap_offset in range(1, min(int(laps_remaining), 15)):
            my_pace = self.deg_model.predict_lap_time(circuit, new_compound, lap_offset, track_temp)
            their_pace = self.deg_model.predict_lap_time(
                circuit, their_compound, their_tyre_life + lap_offset, track_temp
            )
            if my_pace and their_pace:
                cumulative_gain += (their_pace - my_pace)
            if cumulative_gain >= gap_after_pit:
                laps_to_close = lap_offset
                break

        viable = laps_to_close <= min(laps_remaining, 10)
        projected_gain = cumulative_gain - gap_after_pit

        return viable, float(laps_to_close), float(projected_gain)

    def overcut_viable(self, circuit, gap_behind_s, pit_loss_s,
                       my_compound, my_tyre_life,
                       their_compound, their_new_compound,
                       laps_remaining, track_temp=None):
        """
        Check if overcut is viable (they pit first, I stay out).
        Returns (viable: bool, margin_s: float)
        """
        if gap_behind_s is None:
            return False, None

        # They pit: lose pit_loss time, gain fresh tyres
        # I stay out: maintain position but on older tyres
        # Overcut works if: even after they get fresh tyres, they can't catch me
        # before I eventually pit myself

        their_fresh_pace = self.deg_model.predict_lap_time(circuit, their_new_compound, 1, track_temp)
        my_current_pace = self.deg_model.predict_lap_time(circuit, my_compound, my_tyre_life, track_temp)

        if their_fresh_pace is None or my_current_pace is None:
            return False, None

        # After they pit, gap opens to gap_behind + pit_loss
        gap_after_their_pit = gap_behind_s + pit_loss_s

        # Their pace advantage on fresh tyres
        their_adv = my_current_pace - their_fresh_pace
        if their_adv <= 0:
            # I'm faster even on old tyres, overcut is great
            return True, float(gap_after_their_pit)

        laps_to_catch = gap_after_their_pit / their_adv if their_adv > 0 else 999

        # Overcut is viable if they need more laps to catch than we plan to stay out
        extend_laps = min(5, laps_remaining)  # typical overcut extension
        viable = laps_to_catch > extend_laps
        margin = gap_after_their_pit - their_adv * extend_laps

        return viable, float(margin)

    def best_pit_compound(self, circuit, laps_remaining, compounds_used,
                          available_compounds=None, track_temp=None):
        """Recommend best compound for next stint."""
        if available_compounds is None:
            all_compounds = {"SOFT", "MEDIUM", "HARD"}
            used_set = set(compounds_used.split(",")) if compounds_used else set()
            # Must use at least 2 different dry compounds per race
            if len(used_set) == 0:
                available_compounds = list(all_compounds)
            else:
                # Prefer unused compound if only 1 used so far
                unused = all_compounds - used_set
                available_compounds = list(unused) if unused else list(all_compounds)

        best = None
        best_score = float("inf")

        for compound in available_compounds:
            stint_len = self.deg_model.expected_stint_length(circuit, compound)
            if stint_len < laps_remaining * 0.3 and compound == "SOFT" and laps_remaining > 15:
                continue  # soft won't last

            # Score: projected total time over remaining laps on this compound
            total_time = 0
            for lap in range(1, min(laps_remaining + 1, stint_len + 1)):
                t = self.deg_model.predict_lap_time(circuit, compound, lap, track_temp)
                if t:
                    total_time += t
                else:
                    total_time += 95  # fallback

            # Penalize if compound won't last
            if stint_len < laps_remaining:
                total_time += 22  # another pit stop penalty

            if total_time < best_score:
                best_score = total_time
                best = compound

        return best
