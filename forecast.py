"""Prediction helpers shared by the dashboard and state-change tests."""
from __future__ import annotations

import numpy as np
import pandas as pd

from train_model import FEATURES


def build_prediction_features(current: dict | pd.Series, profile: dict | pd.Series) -> pd.DataFrame:
    """Build features only from the current simulated reading and patient profile."""
    current_values = current.to_dict() if isinstance(current, pd.Series) else dict(current)
    profile_values = profile.to_dict() if isinstance(profile, pd.Series) else dict(profile)
    return pd.DataFrame([{**current_values, **profile_values}])[FEATURES]


def predict_current_state(artifact: dict, current: dict | pd.Series,
                          profile: dict | pd.Series) -> float:
    features = build_prediction_features(current, profile)
    if artifact["metrics"]["model"].startswith("NumpyRidge"):
        features = features.to_numpy(dtype=float)
    return float(artifact["model"].predict(features)[0])


def advance_index(index: int, length: int, steps: int = 1) -> int:
    if length < 1 or steps < 0:
        raise ValueError("length must be positive and steps must be non-negative")
    return min(max(0, int(index)) + int(steps), length - 1)
