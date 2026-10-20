"""GlucoTwin: synthetic-only educational glucose forecasting dashboard."""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from train_model import FEATURES

ROOT = Path(__file__).resolve().parent


@st.cache_data
def load_data():
    ehr = pd.read_csv(ROOT / "data" / "patients.csv")
    readings = pd.read_csv(ROOT / "data" / "sensor_readings.csv", parse_dates=["timestamp"])
    readings["timestamp"] = pd.to_datetime(readings["timestamp"], utc=True)
    return ehr, readings


@st.cache_resource
def load_model():
    path = ROOT / "models" / "glucose_model.joblib"
    if not path.exists():
        raise FileNotFoundError("Model artifact missing. Run: python train_model.py")
    try:
        import joblib
        return joblib.load(path)
    except ImportError:
        with path.open("rb") as stream:
            return pickle.load(stream)


st.set_page_config(page_title="GlucoTwin | Synthetic Digital Twin", page_icon="🧬", layout="wide")
st.title("GlucoTwin")
st.caption("Synthetic digital twin prototype | Research and education only")
st.warning("All profiles and sensor readings on this page are synthetic. Predictions are experimental and are not medical advice, diagnosis, or treatment guidance.")

try:
    patients, sensors = load_data()
    artifact = load_model()
    metrics = artifact["metrics"]
except (FileNotFoundError, ValueError, OSError, KeyError) as exc:
    st.error(f"Unable to load required project data: {exc}")
    st.stop()

patient_id = st.sidebar.selectbox("Synthetic patient", patients.patient_id.tolist())
profile = patients.loc[patients.patient_id == patient_id].iloc[0]
history = sensors.loc[sensors.patient_id == patient_id].sort_values("timestamp").reset_index(drop=True)
if history.empty:
    st.error("No sensor history exists for the selected patient.")
    st.stop()

if "sim_index" not in st.session_state or st.session_state.get("sim_patient") != patient_id:
    st.session_state.sim_index = max(0, len(history) - 96)
    st.session_state.sim_patient = patient_id
advance = st.sidebar.button("Advance sensor stream by 15 minutes")
if advance:
    st.session_state.sim_index = min(st.session_state.sim_index + 1, len(history) - 1)
idx = int(np.clip(st.session_state.sim_index, 0, len(history) - 1))
current = history.iloc[idx]
feature_row = pd.DataFrame([{**current.to_dict(), **profile.to_dict()}])[FEATURES]
prediction = float(artifact["model"].predict(feature_row.to_numpy(float) if metrics["model"].startswith("NumpyRidge") else feature_row)[0])
forecast_time = current.timestamp + pd.Timedelta(hours=2)

left, right = st.columns([1, 2])
with left:
    st.subheader("Virtual patient profile")
    st.markdown("**Source: synthetic EHR profile**")
    st.write(f"**ID:** `{profile.patient_id}`")
    st.write(f"**Age:** {int(profile.age_years)} years | **Sex:** {profile.sex}")
    st.write(f"**BMI:** {profile.bmi_kg_m2} kg/m² | **HbA1c:** {profile.hba1c_pct}%")
    st.write(f"**Duration:** {int(profile.diabetes_duration_years)} years")
    st.write(f"**Medication category:** {profile.medication_category}")
    st.subheader("Current simulated state")
    st.markdown("**Source: simulated sensor stream**")
    st.metric("Glucose", f"{current.glucose_mg_dl:.0f} mg/dL")
    st.write(f"Heart rate: {current.heart_rate_bpm:.0f} bpm")
    st.write(f"Activity: {current.activity_min_15m:.0f} min / 15 min")
    st.write(f"Sleep flag: {'asleep' if current.sleeping else 'awake'}")
    st.caption(f"Stream position: {current.timestamp.strftime('%Y-%m-%d %H:%M UTC')} (simulated)")
with right:
    st.subheader("Two-hour glucose forecast")
    st.metric("Predicted glucose", f"{prediction:.0f} mg/dL", help="Model estimate at the current simulated timestamp plus 120 minutes.")
    st.caption(f"Prediction target time: {forecast_time.strftime('%Y-%m-%d %H:%M UTC')} | **Prediction, not an observed value**")
    visible = history.iloc[max(0, idx - 95):idx + 1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=visible.timestamp, y=visible.glucose_mg_dl, name="Simulated sensor values", mode="lines", line={"color":"#58a6ff"}))
    fig.add_trace(go.Scatter(x=[forecast_time], y=[prediction], name="Model prediction (+2h)", mode="markers", marker={"color":"#ffb454","size":12,"symbol":"diamond"}))
    fig.update_layout(height=370, margin={"l":10,"r":10,"t":25,"b":10}, yaxis_title="Glucose (mg/dL)", xaxis_title="Timestamp (UTC)", legend={"orientation":"h"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Model evaluation")
st.caption("Held-out later timestamps from synthetic data. This is an engineering demonstration, not clinical validation.")
m1, m2, m3 = st.columns(3)
m1.metric("Model MAE", f"{metrics['model_mae_mg_dl']:.1f} mg/dL")
m2.metric("Last-value baseline MAE", f"{metrics['baseline_last_value_mae_mg_dl']:.1f} mg/dL")
m3.metric("Held-out rows", f"{metrics['test_rows']:,}")
st.write(f"Model: {metrics['model']} | Split cutoff: {metrics['cutoff_utc']} | Horizon: 120 minutes")
st.caption("Observed data: none. Every displayed profile and sensor point is simulated. The forecast is a model prediction.")
