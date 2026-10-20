"""Train and chronologically evaluate a synthetic 2-hour glucose model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pickle
from model_utils import NumpyRidge
try:
    import joblib
except ImportError:
    joblib = None
try:
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error
except ImportError:
    HistGradientBoostingRegressor = None
    mean_absolute_error = None

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
MODEL = ROOT / "models" / "glucose_model.joblib"
FEATURES = ["glucose_mg_dl", "heart_rate_bpm", "activity_min_15m", "sleeping",
            "hour_sin", "hour_cos", "age_years", "bmi_kg_m2", "hba1c_pct",
            "diabetes_duration_years"]
TARGET = "target_glucose_2h_mg_dl"


def build_training_frame(sensor: pd.DataFrame, patients: pd.DataFrame) -> pd.DataFrame:
    required_sensor = {"patient_id", "timestamp", *FEATURES[:6]}
    missing = required_sensor - set(sensor.columns)
    if missing:
        raise ValueError(f"sensor data missing columns: {sorted(missing)}")
    sensor = sensor.copy()
    sensor["timestamp"] = pd.to_datetime(sensor["timestamp"], utc=True, errors="coerce")
    if sensor["timestamp"].isna().any():
        raise ValueError("sensor timestamps must be valid")
    sensor = sensor.sort_values(["patient_id", "timestamp"])
    # 2 hours = 8 samples at 15-minute cadence. Validate exact cadence so no
    # irregular interval is silently represented as two hours.
    delta = sensor.groupby("patient_id")["timestamp"].diff()
    if (delta.dropna() != pd.Timedelta(minutes=15)).any():
        raise ValueError("sensor readings must be spaced exactly 15 minutes apart")
    sensor[TARGET] = sensor.groupby("patient_id")["glucose_mg_dl"].shift(-8)
    frame = sensor.merge(patients, on="patient_id", how="left", validate="many_to_one")
    frame = frame.dropna(subset=FEATURES + [TARGET]).copy()
    return frame


def train(data_dir: str | Path = DATA, model_path: str | Path = MODEL) -> dict:
    data_dir = Path(data_dir)
    patients = pd.read_csv(data_dir / "patients.csv")
    sensor = pd.read_csv(data_dir / "sensor_readings.csv")
    frame = build_training_frame(sensor, patients)
    # Hold out final 20% of time per patient. No random row split or future data leakage.
    frame = frame.sort_values(["timestamp", "patient_id"]).reset_index(drop=True)
    cutoff = frame["timestamp"].quantile(.8)
    train_df, test_df = frame[frame.timestamp <= cutoff], frame[frame.timestamp > cutoff]
    if train_df.empty or test_df.empty:
        raise ValueError("chronological split produced an empty partition")
    X_train, y_train = train_df[FEATURES], train_df[TARGET]
    X_test, y_test = test_df[FEATURES], test_df[TARGET]
    baseline_pred = test_df["glucose_mg_dl"].to_numpy()
    if mean_absolute_error:
        baseline = mean_absolute_error(y_test, baseline_pred)
    else:
        baseline = np.mean(np.abs(y_test.to_numpy() - baseline_pred))
    if HistGradientBoostingRegressor:
        model = HistGradientBoostingRegressor(max_iter=120, learning_rate=.08, max_leaf_nodes=20,
                                              l2_regularization=2.0, random_state=2026)
        model.fit(X_train, y_train)
        model_name = "HistGradientBoostingRegressor"
    else:
        # Small NumPy ridge fallback keeps the app and artifact reproducible in
        # offline environments. Normalization is learned from training rows only.
        model = NumpyRidge(alpha=35.0).fit(X_train.to_numpy(float), y_train.to_numpy(float))
        model_name = "NumpyRidge (offline fallback; install requirements for scikit-learn model)"
    pred = model.predict(X_test.to_numpy(float) if model_name.startswith("NumpyRidge") else X_test)
    metrics = {"target": "glucose_mg_dl at timestamp + 2 hours",
               "horizon_minutes": 120, "sample_cadence_minutes": 15,
               "split": "chronological per pooled timestamp; earliest 80% train, latest 20% test",
               "cutoff_utc": cutoff.isoformat(), "train_rows": len(train_df),
               "test_rows": len(test_df), "baseline_last_value_mae_mg_dl": round(float(baseline), 3),
               "model_mae_mg_dl": round(float(mean_absolute_error(y_test, pred) if mean_absolute_error else np.mean(np.abs(y_test.to_numpy()-pred))), 3),
               "model": model_name, "synthetic_only": True}
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {"model": model, "features": FEATURES, "metrics": metrics}
    if joblib:
        joblib.dump(artifact, model_path)
    else:
        with model_path.open("wb") as stream:
            pickle.dump(artifact, stream)
    model_path.with_name("metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (data_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--model-path", type=Path, default=MODEL)
    args = parser.parse_args()
    print(json.dumps(train(args.data_dir, args.model_path), indent=2))
