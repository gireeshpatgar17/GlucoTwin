from pathlib import Path

import pandas as pd
import pytest

from generate_data import generate_data
from train_model import build_training_frame, train


def test_generation_is_reproducible(tmp_path):
    e1, s1 = generate_data(tmp_path / "one", patients=5, days=3, seed=12)
    e2, s2 = generate_data(tmp_path / "two", patients=5, days=3, seed=12)
    pd.testing.assert_frame_equal(e1, e2)
    pd.testing.assert_frame_equal(s1, s2)
    assert len(s1) == 5 * 3 * 24 * 4
    assert set(s1.data_status) == {"simulated"}


def test_two_hour_target_and_chronological_training(tmp_path):
    data = tmp_path / "data"
    generate_data(data, patients=8, days=5, seed=21)
    patients = pd.read_csv(data / "patients.csv")
    sensor = pd.read_csv(data / "sensor_readings.csv")
    frame = build_training_frame(sensor, patients)
    first = frame.iloc[0]
    assert first.target_glucose_2h_mg_dl == pytest.approx(
        sensor[(sensor.patient_id == first.patient_id)].iloc[8].glucose_mg_dl)
    metrics = train(data, tmp_path / "model" / "glucose_model.joblib")
    assert metrics["horizon_minutes"] == 120
    assert metrics["train_rows"] > metrics["test_rows"]
    assert metrics["model_mae_mg_dl"] >= 0
    assert (tmp_path / "model" / "metrics.json").exists()


def test_irregular_cadence_rejected():
    sensor = pd.DataFrame({"patient_id":["a"]*10,
        "timestamp":pd.date_range("2025-01-01", periods=10, freq="15min").astype(str),
        "glucose_mg_dl":[100.]*10,"heart_rate_bpm":[70.]*10,
        "activity_min_15m":[0.]*10,"sleeping":[0]*10,"hour_sin":[0.]*10,"hour_cos":[1.]*10})
    sensor.loc[2,"timestamp"] = "2025-01-01 00:35:00+00:00"
    patient = pd.DataFrame({"patient_id":["a"],"age_years":[50],"bmi_kg_m2":[30],
        "hba1c_pct":[7.],"diabetes_duration_years":[5]})
    with pytest.raises(ValueError, match="exactly 15 minutes"):
        build_training_frame(sensor, patient)
