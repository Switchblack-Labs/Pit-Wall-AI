"""
Tyre degradation model using scipy curve fitting.
Fits per (circuit, compound) from historical stint data.
"""
import numpy as np
from scipy.optimize import curve_fit
from ml_engine.data.schema import get_connection


def _deg_func(tyre_life, base_pace, deg_coeff, deg_exp):
    """Degradation model: lap_time = base_pace + deg_coeff * tyre_life^deg_exp"""
    return base_pace + deg_coeff * np.power(tyre_life, deg_exp)


def _linear_deg(tyre_life, base_pace, deg_rate):
    """Simple linear: lap_time = base_pace + deg_rate * tyre_life"""
    return base_pace + deg_rate * tyre_life


class DegradationModel:
    def __init__(self):
        self.curves = {}  # (circuit, compound) -> params
        self.temp_coeffs = {}  # circuit -> temp_sensitivity

    def fit_all(self, conn=None):
        """Fit degradation curves for all (circuit, compound) combinations."""
        if conn is None:
            conn = get_connection()

        combos = conn.execute("""
            SELECT DISTINCT r.circuit, s.compound
            FROM stints s
            JOIN races r ON s.race_id = r.race_id
            WHERE s.compound IN ('SOFT', 'MEDIUM', 'HARD')
            AND s.num_laps >= 5
        """).fetchall()

        for combo in combos:
            circuit, compound = combo["circuit"], combo["compound"]
            self._fit_curve(conn, circuit, compound)

        self._fit_temp_sensitivity(conn)
        return len(self.curves)

    def _fit_curve(self, conn, circuit, compound):
        """Fit deg curve for a specific circuit+compound."""
        # Get all clean laps from stints of this compound at this circuit
        rows = conn.execute("""
            SELECT l.tyre_life, l.lap_time_ms
            FROM laps l
            JOIN races r ON l.race_id = r.race_id
            JOIN stints s ON l.race_id = s.race_id AND l.driver = s.driver
                AND l.lap BETWEEN s.start_lap AND s.end_lap
            WHERE r.circuit=? AND s.compound=?
            AND l.is_accurate=1 AND l.lap_time_ms IS NOT NULL
            AND l.track_status IN ('1', '2')
            AND l.is_pit_out=0 AND l.is_pit_in=0
            AND l.tyre_life IS NOT NULL AND l.tyre_life > 0
        """, (circuit, compound)).fetchall()

        if len(rows) < 10:
            return

        tyre_lives = np.array([r["tyre_life"] for r in rows], dtype=float)
        lap_times = np.array([r["lap_time_ms"] / 1000.0 for r in rows])

        # Filter outliers (remove laps > 3 std from median)
        median_time = np.median(lap_times)
        std_time = np.std(lap_times)
        mask = np.abs(lap_times - median_time) < 3 * std_time
        tyre_lives = tyre_lives[mask]
        lap_times = lap_times[mask]

        if len(tyre_lives) < 8:
            return

        # Try power fit first, fall back to linear
        try:
            p0 = [np.min(lap_times), 0.01, 1.5]
            popt, _ = curve_fit(_deg_func, tyre_lives, lap_times, p0=p0,
                                maxfev=5000,
                                bounds=([np.min(lap_times) - 5, 0, 0.5],
                                        [np.min(lap_times) + 5, 1.0, 3.0]))
            residuals = lap_times - _deg_func(tyre_lives, *popt)
            rmse = np.sqrt(np.mean(residuals**2))
            self.curves[(circuit, compound)] = {
                "type": "power", "params": popt.tolist(), "rmse": rmse,
                "n_samples": len(tyre_lives)
            }
        except (RuntimeError, ValueError):
            try:
                popt, _ = curve_fit(_linear_deg, tyre_lives, lap_times,
                                    p0=[np.min(lap_times), 0.05])
                residuals = lap_times - _linear_deg(tyre_lives, *popt)
                rmse = np.sqrt(np.mean(residuals**2))
                self.curves[(circuit, compound)] = {
                    "type": "linear", "params": popt.tolist(), "rmse": rmse,
                    "n_samples": len(tyre_lives)
                }
            except (RuntimeError, ValueError):
                pass

    def _fit_temp_sensitivity(self, conn):
        """Fit temperature sensitivity coefficient per circuit."""
        circuits = conn.execute("SELECT DISTINCT circuit FROM races").fetchall()

        for row in circuits:
            circuit = row["circuit"]
            data = conn.execute("""
                SELECT w.track_temp, l.lap_time_ms, l.tyre_life, l.compound
                FROM laps l
                JOIN weather w ON l.race_id = w.race_id AND l.lap = w.lap
                JOIN races r ON l.race_id = r.race_id
                WHERE r.circuit=? AND l.is_accurate=1 AND l.lap_time_ms IS NOT NULL
                AND l.track_status='1' AND w.track_temp IS NOT NULL
                AND l.tyre_life BETWEEN 5 AND 15
            """, (circuit,)).fetchall()

            if len(data) < 20:
                self.temp_coeffs[circuit] = 0.0
                continue

            temps = np.array([d["track_temp"] for d in data])
            times = np.array([d["lap_time_ms"] / 1000.0 for d in data])

            baseline_temp = np.median(temps)
            try:
                coeffs = np.polyfit(temps - baseline_temp, times, 1)
                self.temp_coeffs[circuit] = {
                    "coeff": float(coeffs[0]),
                    "baseline": float(baseline_temp)
                }
            except (np.linalg.LinAlgError, ValueError):
                self.temp_coeffs[circuit] = {"coeff": 0.0, "baseline": 30.0}

    def predict_lap_time(self, circuit, compound, tyre_life, track_temp=None):
        """Predict lap time for given conditions."""
        key = (circuit, compound)
        if key not in self.curves:
            # Fall back to any compound at this circuit, or global average
            fallback = [k for k in self.curves if k[0] == circuit]
            if not fallback:
                return None
            key = fallback[0]

        curve = self.curves[key]
        if curve["type"] == "power":
            base_time = _deg_func(tyre_life, *curve["params"])
        else:
            base_time = _linear_deg(tyre_life, *curve["params"])

        # Temperature correction
        if track_temp is not None and circuit in self.temp_coeffs:
            tc = self.temp_coeffs[circuit]
            if isinstance(tc, dict):
                base_time += tc["coeff"] * (track_temp - tc["baseline"])

        return float(base_time)

    def predict_deg_rate(self, circuit, compound, tyre_life, track_temp=None):
        """Predict instantaneous degradation rate (s/lap) at given tyre life."""
        key = (circuit, compound)
        if key not in self.curves:
            return 0.05  # default

        curve = self.curves[key]
        if curve["type"] == "power":
            base, coeff, exp = curve["params"]
            # Derivative: coeff * exp * tyre_life^(exp-1)
            if tyre_life < 1:
                tyre_life = 1
            rate = coeff * exp * (tyre_life ** (exp - 1))
        else:
            rate = curve["params"][1]  # constant linear rate

        # Temperature multiplier
        if track_temp is not None and circuit in self.temp_coeffs:
            tc = self.temp_coeffs[circuit]
            if isinstance(tc, dict) and tc["baseline"] > 0:
                temp_mult = 1.0 + (track_temp - tc["baseline"]) * 0.005
                rate *= max(0.5, min(2.0, temp_mult))

        return float(rate)

    def expected_stint_length(self, circuit, compound, cliff_threshold_s=2.5):
        """How many laps before pace drops by cliff_threshold_s."""
        key = (circuit, compound)
        if key not in self.curves:
            defaults = {"SOFT": 18, "MEDIUM": 28, "HARD": 38}
            return defaults.get(compound, 25)

        for tyre_life in range(1, 60):
            t = self.predict_lap_time(circuit, compound, tyre_life)
            t1 = self.predict_lap_time(circuit, compound, 1)
            if t is not None and t1 is not None and (t - t1) > cliff_threshold_s:
                return tyre_life

        return 50  # no cliff found

    def save(self, path):
        import json
        data = {
            "curves": {f"{k[0]}|{k[1]}": v for k, v in self.curves.items()},
            "temp_coeffs": self.temp_coeffs,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path):
        import json
        with open(path) as f:
            data = json.load(f)
        self.curves = {
            (k.split("|")[0], k.split("|")[1]): v
            for k, v in data["curves"].items()
        }
        self.temp_coeffs = data["temp_coeffs"]
