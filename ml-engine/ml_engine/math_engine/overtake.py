"""
Overtake probability model. Starts with hardcoded circuit values,
then gets replaced by ML model if it beats baseline.
"""
import numpy as np
from ml_engine.config import LOW_OVERTAKE_CIRCUITS, HIGH_OVERTAKE_CIRCUITS
from ml_engine.data.schema import get_connection


# Baseline: derived from 2022-2024 overtake statistics
CIRCUIT_OVERTAKE_RATE = {
    "bahrain": 0.55, "jeddah": 0.52, "albert_park": 0.35,
    "baku": 0.48, "miami": 0.38, "imola": 0.25,
    "monaco": 0.04, "catalunya": 0.22, "montreal": 0.40,
    "silverstone": 0.30, "red_bull_ring": 0.42, "hungaroring": 0.08,
    "spa": 0.50, "zandvoort": 0.10, "monza": 0.65,
    "marina_bay": 0.06, "suzuka": 0.20, "losail": 0.35,
    "americas": 0.32, "mexico_city": 0.28, "interlagos": 0.45,
    "las_vegas": 0.48, "yas_marina": 0.38, "shanghai": 0.45,
}


class OvertakeModel:
    def __init__(self):
        self.circuit_rates = dict(CIRCUIT_OVERTAKE_RATE)
        self.ml_model = None

    def fit_from_data(self, conn=None):
        """Compute overtake rates from actual position change data."""
        if conn is None:
            conn = get_connection()

        circuits = conn.execute("SELECT DISTINCT circuit FROM races").fetchall()
        for row in circuits:
            circuit = row["circuit"]
            # Count laps where position improved vs total laps
            data = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN positions_delta_5 > 0 THEN 1 ELSE 0 END) as gained
                FROM race_states
                WHERE circuit=? AND track_status='1'
                AND gap_ahead_s IS NOT NULL AND gap_ahead_s < 2.0
                AND positions_delta_5 IS NOT NULL
            """, (circuit,)).fetchone()

            if data and data["total"] >= 20:
                rate = data["gained"] / data["total"]
                self.circuit_rates[circuit] = float(rate)

    def predict(self, circuit, gap_ahead_s, my_compound, their_compound,
                my_tyre_life, their_tyre_life, drs_available=True):
        """
        Predict probability of overtaking the car ahead.
        """
        if self.ml_model is not None:
            return self._ml_predict(circuit, gap_ahead_s, my_compound,
                                    their_compound, my_tyre_life, their_tyre_life, drs_available)

        base_rate = self.circuit_rates.get(circuit, 0.25)

        if gap_ahead_s is None:
            return 0.0

        # Modifiers
        # Gap: closer = easier
        if gap_ahead_s < 0.5:
            gap_mod = 1.3
        elif gap_ahead_s < 1.0:
            gap_mod = 1.1
        elif gap_ahead_s < 1.5:
            gap_mod = 0.9
        elif gap_ahead_s < 2.0:
            gap_mod = 0.5
        else:
            gap_mod = 0.1

        # Tyre advantage
        tyre_delta = their_tyre_life - my_tyre_life
        if tyre_delta > 10:
            tyre_mod = 1.4
        elif tyre_delta > 5:
            tyre_mod = 1.2
        elif tyre_delta < -5:
            tyre_mod = 0.7
        else:
            tyre_mod = 1.0

        # Compound advantage (softer compound = more grip)
        compound_order = {"SOFT": 0, "MEDIUM": 1, "HARD": 2, "INTERMEDIATE": 1, "WET": 1}
        my_ord = compound_order.get(my_compound, 1)
        their_ord = compound_order.get(their_compound, 1)
        compound_mod = 1.0 + (their_ord - my_ord) * 0.15

        # DRS
        drs_mod = 1.3 if drs_available else 0.8

        prob = base_rate * gap_mod * tyre_mod * compound_mod * drs_mod
        return float(np.clip(prob, 0.0, 0.95))

    def _ml_predict(self, circuit, gap_ahead_s, my_compound, their_compound,
                    my_tyre_life, their_tyre_life, drs_available):
        """Use ML model for prediction."""
        from ml_engine.config import COMPOUND_ENCODING
        features = np.array([[
            hash(circuit) % 100,  # will be properly encoded in training
            gap_ahead_s or 2.0,
            COMPOUND_ENCODING.get(my_compound, 1),
            COMPOUND_ENCODING.get(their_compound, 1),
            my_tyre_life or 10,
            their_tyre_life or 10,
            1.0 if drs_available else 0.0,
        ]])
        return float(self.ml_model.predict_proba(features)[0, 1])

    def set_ml_model(self, model):
        self.ml_model = model

    def can_close_gap(self, circuit, gap_s, pace_advantage_per_lap, laps_remaining):
        """Check if a driver can close a gap and overtake."""
        if pace_advantage_per_lap <= 0:
            return False, 999

        laps_to_close = gap_s / pace_advantage_per_lap
        if laps_to_close > laps_remaining:
            return False, laps_to_close

        overtake_prob = self.circuit_rates.get(circuit, 0.25)
        can_do = overtake_prob > 0.15 and laps_to_close < laps_remaining * 0.8
        return can_do, float(laps_to_close)
