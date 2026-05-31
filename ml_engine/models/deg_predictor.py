"""
ML-based tyre degradation predictor using XGBoost.
Competes against scipy curve fit baseline.
Only used if it beats the baseline on held-out data.
"""
import numpy as np
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
from ml_engine.data.schema import get_connection
from ml_engine.config import MODEL_DIR, COMPOUND_ENCODING


class DegPredictor:
    def __init__(self):
        self.model = None
        self.circuit_encoder = LabelEncoder()
        self.feature_cols = [
            "circuit_enc", "compound_enc", "tyre_life",
            "track_temp", "air_temp", "rainfall",
            "fuel_load_proxy", "laps_remaining_pct"
        ]
        self.baseline_rmse = None
        self.ml_rmse = None
        self.beats_baseline = False

    def _load_training_data(self, conn):
        """Load and prepare training data from race_states."""
        rows = conn.execute("""
            SELECT rs.circuit, rs.compound, rs.tyre_life,
                   rs.track_temp, rs.air_temp, rs.rainfall,
                   rs.laps_remaining, rs.total_laps,
                   rs.lap_time_s, rs.deg_rate,
                   rs.lap_time_delta_vs_fresh
            FROM race_states rs
            WHERE rs.lap_time_s IS NOT NULL
            AND rs.compound IN ('SOFT', 'MEDIUM', 'HARD')
            AND rs.tyre_life IS NOT NULL AND rs.tyre_life > 0
            AND rs.track_status = '1'
            AND rs.lap_time_delta_vs_fresh IS NOT NULL
        """).fetchall()

        if len(rows) < 100:
            return None

        df = pd.DataFrame([dict(r) for r in rows])

        # Feature engineering
        self.circuit_encoder.fit(df["circuit"].unique())
        df["circuit_enc"] = self.circuit_encoder.transform(df["circuit"])
        df["compound_enc"] = df["compound"].map(COMPOUND_ENCODING).fillna(1)
        df["fuel_load_proxy"] = df["laps_remaining"] / df["total_laps"]  # proxy for fuel
        df["laps_remaining_pct"] = df["laps_remaining"] / df["total_laps"]

        # Fill nulls
        df["track_temp"] = df["track_temp"].fillna(df["track_temp"].median())
        df["air_temp"] = df["air_temp"].fillna(df["air_temp"].median())
        df["rainfall"] = df["rainfall"].fillna(0)

        # Target: lap_time_delta_vs_fresh (how much slower than stint start)
        df["target"] = df["lap_time_delta_vs_fresh"]

        return df

    def train(self, conn=None):
        """Train the XGBoost deg predictor."""
        import xgboost as xgb

        if conn is None:
            conn = get_connection()

        df = self._load_training_data(conn)
        if df is None:
            print("Not enough data to train deg predictor")
            return False

        X = df[self.feature_cols].values
        y = df["target"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Baseline: per (circuit, compound) mean deg rate * tyre_life
        baseline_preds = []
        for idx in range(len(X_test)):
            circuit_enc = int(X_test[idx, 0])
            compound_enc = int(X_test[idx, 1])
            tyre_life = X_test[idx, 2]

            mask = (X_train[:, 0] == circuit_enc) & (X_train[:, 1] == compound_enc)
            if mask.sum() > 5:
                avg_rate = np.mean(y_train[mask]) / np.mean(X_train[mask, 2])
                baseline_preds.append(avg_rate * tyre_life)
            else:
                baseline_preds.append(np.mean(y_train) / np.mean(X_train[:, 2]) * tyre_life)

        self.baseline_rmse = float(np.sqrt(mean_squared_error(y_test, baseline_preds)))

        # XGBoost
        self.model = xgb.XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            tree_method="hist",
            device="cuda",  # use GPU
            random_state=42,
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=50,
        )

        ml_preds = self.model.predict(X_test)
        self.ml_rmse = float(np.sqrt(mean_squared_error(y_test, ml_preds)))
        ml_mae = float(mean_absolute_error(y_test, ml_preds))

        self.beats_baseline = self.ml_rmse < self.baseline_rmse

        print(f"\nDeg Predictor Results:")
        print(f"  Baseline RMSE: {self.baseline_rmse:.4f}s")
        print(f"  XGBoost RMSE:  {self.ml_rmse:.4f}s")
        print(f"  XGBoost MAE:   {ml_mae:.4f}s")
        print(f"  Beats baseline: {self.beats_baseline}")
        print(f"  Improvement:   {(1 - self.ml_rmse/self.baseline_rmse)*100:.1f}%")

        # Feature importance
        importances = self.model.feature_importances_
        for feat, imp in sorted(zip(self.feature_cols, importances), key=lambda x: -x[1]):
            print(f"    {feat}: {imp:.3f}")

        return self.beats_baseline

    def predict(self, circuit, compound, tyre_life, track_temp=None,
                air_temp=None, rainfall=0, laps_remaining=20, total_laps=57):
        """Predict lap time delta vs fresh."""
        if self.model is None:
            return None

        circuit_enc = 0
        try:
            circuit_enc = self.circuit_encoder.transform([circuit])[0]
        except ValueError:
            pass

        compound_enc = COMPOUND_ENCODING.get(compound, 1)
        fuel_proxy = laps_remaining / max(total_laps, 1)

        X = np.array([[
            circuit_enc, compound_enc, tyre_life,
            track_temp or 35, air_temp or 25, rainfall,
            fuel_proxy, fuel_proxy
        ]])

        return float(self.model.predict(X)[0])

    def save(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, os.path.join(MODEL_DIR, "deg_predictor.pkl"))
        joblib.dump(self.circuit_encoder, os.path.join(MODEL_DIR, "deg_circuit_encoder.pkl"))
        meta = {
            "baseline_rmse": self.baseline_rmse,
            "ml_rmse": self.ml_rmse,
            "beats_baseline": self.beats_baseline,
            "feature_cols": self.feature_cols,
        }
        joblib.dump(meta, os.path.join(MODEL_DIR, "deg_meta.pkl"))

    def load(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, "deg_predictor.pkl"))
        self.circuit_encoder = joblib.load(os.path.join(MODEL_DIR, "deg_circuit_encoder.pkl"))
        meta = joblib.load(os.path.join(MODEL_DIR, "deg_meta.pkl"))
        self.baseline_rmse = meta["baseline_rmse"]
        self.ml_rmse = meta["ml_rmse"]
        self.beats_baseline = meta["beats_baseline"]
