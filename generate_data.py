"""Create deterministic synthetic EHR and sensor records for GlucoTwin.

All records are fictional and generated from seeded distributions; they are not
clinical data and must not be used for clinical decisions.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_OUT = Path(__file__).resolve().parent / "data"


def generate_data(out_dir: str | Path = DEFAULT_OUT, patients: int = 60,
                  days: int = 21, seed: int = 2026) -> tuple[pd.DataFrame, pd.DataFrame]:
    if patients < 5 or days < 3:
        raise ValueError("patients must be >= 5 and days must be >= 3")
    rng = np.random.default_rng(seed)
    profiles = []
    for i in range(patients):
        age = int(rng.integers(35, 81))
        sex = str(rng.choice(["Female", "Male"]))
        bmi = round(float(np.clip(rng.normal(30, 5), 19, 46)), 1)
        hba1c = round(float(np.clip(rng.normal(7.8 + (bmi - 30) * .025, 1.2), 5.8, 12.5)), 1)
        baseline = float(np.clip(112 + (hba1c - 6.5) * 17 + (bmi - 27) * .55, 95, 260))
        profiles.append({"patient_id": f"SYN-{i+1:03d}", "age_years": age,
                         "sex": sex, "bmi_kg_m2": bmi, "hba1c_pct": hba1c,
                         "diabetes_duration_years": int(rng.integers(1, 26)),
                         "medication_category": str(rng.choice(["Lifestyle", "Oral", "Insulin"], p=[.15,.62,.23])),
                         "baseline_glucose_mg_dl": round(baseline, 1)})
    ehr = pd.DataFrame(profiles)
    freq = "15min"
    periods = days * 24 * 4
    end = pd.Timestamp("2026-10-19 23:45:00", tz="UTC")
    timestamps = pd.date_range(end=end, periods=periods, freq=freq)
    records = []
    for profile in profiles:
        n = len(timestamps)
        tod = timestamps.hour.to_numpy() + timestamps.minute.to_numpy() / 60
        meal = np.zeros(n)
        for hour in (8, 13, 19):
            delta = np.minimum((tod-hour) % 24, (hour-tod) % 24)
            meal += 34 * np.exp(-delta**2 / .22)
        circadian = 7 * np.sin(2 * np.pi * (tod - 5) / 24)
        activity = np.clip(rng.gamma(1.3, 22, n), 0, 180)
        sleeping = ((tod >= 23) | (tod < 7)).astype(int)
        heart_rate = np.clip(68 + activity * .22 + rng.normal(0, 5, n) - sleeping * 5, 48, 150)
        glucose = profile["baseline_glucose_mg_dl"] + circadian + meal - activity * .09 + rng.normal(0, 10, n)
        # Mild temporal autocorrelation; values remain plausible synthetic observations.
        for j in range(1, n):
            glucose[j] = .72 * glucose[j-1] + .28 * glucose[j]
        glucose = np.clip(glucose, 65, 360)
        records.append(pd.DataFrame({
            "patient_id": profile["patient_id"], "timestamp": timestamps,
            "glucose_mg_dl": np.round(glucose, 1), "heart_rate_bpm": np.round(heart_rate, 1),
            "activity_min_15m": np.round(activity, 1), "sleeping": sleeping,
            "hour_sin": np.sin(2*np.pi*tod/24), "hour_cos": np.cos(2*np.pi*tod/24),
            "data_status": "simulated"}))
    sensors = pd.concat(records, ignore_index=True)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ehr.to_csv(out / "patients.csv", index=False)
    sensors.to_csv(out / "sensor_readings.csv", index=False)
    return ehr, sensors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--patients", type=int, default=60)
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    e, s = generate_data(args.out_dir, args.patients, args.days, args.seed)
    print(f"Wrote {len(e)} synthetic patient profiles and {len(s):,} simulated readings to {args.out_dir}")
