"""
ML-based overtake probability model using LightGBM.
Binary classification: did position improve in next 5 laps?
"""
import numpy as np
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, roc_auc_score, precision_score,
                             recall_score, f1_score, log_loss)
from sklearn.preprocessing import LabelEncoder
from ml_engine.data.schema import get_connection
from ml_engine.config import MODEL_DIR, COMPOUND_ENCODING
from ml_engine.math_engine.overtake import OvertakeModel, CIRCUIT_OVERTAKE_RATE


class OvertakePredictor:
    def __init__(self):
        self.model = None
        self.circuit_encoder = LabelEncoder()
        self.feature_cols = [
            "circuit_enc", "gap_ahead_s", "compound_enc", "compound_ahead_enc",
            "tyre_life", "tyre_life_ahead", "tyre_life_delta",
            "deg_rate", "position", "laps_remaining_pct",
            "track_temp", "rainfall"
        ]
        self.baseline_auc = None
        self.ml_auc = None
        self.beats_baseline = False

    def _load_training_data(self, conn):
        """Load training data: situations where driver is close to car ahead."""
        rows = conn.execute("""
            SELECT rs1.circuit, rs1.gap_ahead_s, rs1.compound, rs1.tyre_life,
                   rs1.deg_rate, rs1.position, rs1.laps_remaining, rs1.total_laps,
                   rs1.track_temp, rs1.rainfall, rs1.positions_delta_5,
                   rs2.compound as compound_ahead, rs2.tyre_life as tyre_life_ahead
            FROM race_states rs1
            LEFT JOIN race_states rs2
                ON rs1.race_id = rs2.race_id AND rs1.lap = rs2.lap
                AND rs2.position = rs1.position - 1
            WHERE rs1.gap_ahead_s IS NOT NULL AND rs1.gap_ahead_s < 3.0
            AND rs1.gap_ahead_s > 0
            AND rs1.track_status = '1'
            AND rs1.positions_delta_5 IS NOT NULL
            AND rs1.position > 1
        """).fetchall()

        if len(rows) < 100:
            return None

        df = pd.DataFrame([dict(r) for r in rows])

        # Target: did position improve?
        df["overtook"] = (df["positions_delta_5"] > 0).astype(int)

        # Encode
        self.circuit_encoder.fit(df["circuit"].unique())
        df["circuit_enc"] = self.circuit_encoder.transform(df["circuit"])
        df["compound_enc"] = df["compound"].map(COMPOUND_ENCODING).fillna(1)
        df["compound_ahead_enc"] = df["compound_ahead"].map(COMPOUND_ENCODING).fillna(1)
        df["tyre_life_ahead"] = df["tyre_life_ahead"].fillna(df["tyre_life"])
        df["tyre_life_delta"] = df["tyre_life_ahead"] - df["tyre_life"]
        df["laps_remaining_pct"] = df["laps_remaining"] / df["total_laps"]
        df["track_temp"] = df["track_temp"].fillna(df["track_temp"].median())
        df["rainfall"] = df["rainfall"].fillna(0)
        df["deg_rate"] = df["deg_rate"].fillna(0)

        return df

    def train(self, conn=None):
        """Train the LightGBM overtake predictor."""
        import lightgbm as lgb

        if conn is None:
            conn = get_connection()

        df = self._load_training_data(conn)
        if df is None:
            print("Not enough data to train overtake model")
            return False

        X = df[self.feature_cols].values
        y = df["overtook"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Baseline: hardcoded circuit rate
        baseline_model = OvertakeModel()
        baseline_preds = []
        for idx in range(len(X_test)):
            circuit_enc = int(X_test[idx, 0])
            # Reverse encode circuit
            try:
                circuit = self.circuit_encoder.inverse_transform([circuit_enc])[0]
            except (ValueError, IndexError):
                circuit = "unknown"
            rate = CIRCUIT_OVERTAKE_RATE.get(circuit, 0.25)
            baseline_preds.append(rate)

        baseline_preds = np.array(baseline_preds)
        self.baseline_auc = float(roc_auc_score(y_test, baseline_preds))

        # LightGBM
        self.model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            class_weight="balanced",
            random_state=42,
            verbose=-1,
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric="auc",
        )

        ml_preds_proba = self.model.predict_proba(X_test)[:, 1]
        ml_preds = self.model.predict(X_test)

        self.ml_auc = float(roc_auc_score(y_test, ml_preds_proba))
        accuracy = float(accuracy_score(y_test, ml_preds))
        precision = float(precision_score(y_test, ml_preds, zero_division=0))
        recall = float(recall_score(y_test, ml_preds, zero_division=0))
        f1 = float(f1_score(y_test, ml_preds, zero_division=0))

        self.beats_baseline = self.ml_auc > self.baseline_auc

        print(f"\nOvertake Model Results:")
        print(f"  Baseline AUC: {self.baseline_auc:.4f}")
        print(f"  LightGBM AUC: {self.ml_auc:.4f}")
        print(f"  Accuracy:     {accuracy:.4f}")
        print(f"  Precision:    {precision:.4f}")
        print(f"  Recall:       {recall:.4f}")
        print(f"  F1:           {f1:.4f}")
        print(f"  Beats baseline: {self.beats_baseline}")

        # Feature importance
        importances = self.model.feature_importances_
        for feat, imp in sorted(zip(self.feature_cols, importances), key=lambda x: -x[1]):
            print(f"    {feat}: {imp}")

        return self.beats_baseline

    def predict(self, circuit, gap_ahead_s, my_compound, their_compound,
                my_tyre_life, their_tyre_life, deg_rate=0, position=10,
                laps_remaining=20, total_laps=57, track_temp=35, rainfall=0):
        """Predict overtake probability."""
        if self.model is None:
            return None

        circuit_enc = 0
        try:
            circuit_enc = self.circuit_encoder.transform([circuit])[0]
        except ValueError:
            pass

        X = np.array([[
            circuit_enc,
            gap_ahead_s or 2.0,
            COMPOUND_ENCODING.get(my_compound, 1),
            COMPOUND_ENCODING.get(their_compound, 1),
            my_tyre_life or 10,
            their_tyre_life or 10,
            (their_tyre_life or 10) - (my_tyre_life or 10),
            deg_rate or 0,
            position,
            laps_remaining / max(total_laps, 1),
            track_temp or 35,
            rainfall or 0,
        ]])

        return float(self.model.predict_proba(X)[0, 1])

    def save(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, os.path.join(MODEL_DIR, "overtake_model.pkl"))
        joblib.dump(self.circuit_encoder, os.path.join(MODEL_DIR, "overtake_circuit_encoder.pkl"))
        meta = {
            "baseline_auc": self.baseline_auc,
            "ml_auc": self.ml_auc,
            "beats_baseline": self.beats_baseline,
            "feature_cols": self.feature_cols,
        }
        joblib.dump(meta, os.path.join(MODEL_DIR, "overtake_meta.pkl"))

    def load(self):
        self.model = joblib.load(os.path.join(MODEL_DIR, "overtake_model.pkl"))
        self.circuit_encoder = joblib.load(os.path.join(MODEL_DIR, "overtake_circuit_encoder.pkl"))
        meta = joblib.load(os.path.join(MODEL_DIR, "overtake_meta.pkl"))
        self.baseline_auc = meta["baseline_auc"]
        self.ml_auc = meta["ml_auc"]
        self.beats_baseline = meta["beats_baseline"]
