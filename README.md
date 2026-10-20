# GlucoTwin — Digital Twin Challenge 2026

## Submission details

- **Project title:** GlucoTwin — Synthetic Two-Hour Glucose Digital Twin
- **Team members:** [Add team member names]
- **College / institution:** [Add college or institution]
- **Team lead contact:** [Add your email; do not publish personal contact details without consent]
- **Phone:** [Add only if required and voluntarily supplied]
- **Presentation:** [`docs/presentation.pdf`](docs/presentation.pdf)
- **Architecture:** [`docs/architecture.pdf`](docs/architecture.pdf)
- **Demo video:** [Video link to be added after recording]

## Problem statement and healthcare use case

This proof of concept explores how a patient-specific digital twin interface could combine longitudinal context with simulated sensor data to estimate glucose two hours ahead. A future research workflow might help care teams inspect trends and evaluate forecasting concepts. This submission is an engineering demonstration only: its synthetic data, metrics, and predictions are not clinically validated and must not guide care.

## What it does

- Generates fictional patient profiles and timestamped 15-minute glucose, heart-rate, activity, and sleep features.
- Defines the target as sensor glucose at `t + 120 minutes` (eight 15-minute steps).
- Trains on earlier timestamps and evaluates on later timestamps; reports MAE beside a last-value baseline.
- Shows a patient profile, virtual stream state, recent history, prediction and actual run metrics in Streamlit.
- Advances the simulated stream in 15-minute increments. Labels EHR profile, simulated sensor values, and prediction separately.

## Technical stack and model

Python, Streamlit, pandas, NumPy, scikit-learn, Plotly, pytest, and joblib. The preferred model is `HistGradientBoostingRegressor`; if scikit-learn is unavailable, the training script uses a standardized NumPy ridge fallback and Python pickle so offline generation and evaluation remain possible. Install the listed dependencies to reproduce the preferred model. No paid APIs, external health services, cloud database, or Docker are used.

## Evaluation results

The generated run used 60 profiles and 120,960 15-minute readings. Its chronological holdout contained 96,420 training and 24,060 test rows, with cutoff `2026-10-15T17:30:00+00:00`. The offline NumPy ridge fallback achieved **5.048 mg/dL MAE**; the current-glucose persistence baseline achieved **8.567 mg/dL MAE**. This result describes only the deterministic synthetic generator and is not clinical performance. Full run details are saved in [`data/metrics.json`](data/metrics.json) and `models/metrics.json`.

## Setup

Use Python 3.10–3.13 (the declared dependencies may not yet support newer interpreter versions). Create and activate a virtual environment, then run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_data.py
python train_model.py
pytest -q
streamlit run app.py
```

The checked-in CSVs and `models/glucose_model.joblib` are generated using seed 2026. Re-run the commands above to regenerate. Offline fallback note: if scikit-learn/joblib are not installed, `train_model.py` uses NumPy ridge and pickle; app runtime still requires Streamlit and Plotly.

## Architecture

`generate_data.py` creates synthetic EHR and sensor CSVs. `train_model.py` aligns each row with the reading eight intervals (120 minutes) later, joins patient features, uses a chronological pooled-time holdout, compares against current-glucose persistence, and stores the model and metrics. `app.py` loads these local artifacts and displays a simulated stream and forecast. See [`docs/architecture.pdf`](docs/architecture.pdf).

## Limitations and medical-use notice

All people, records, sensor values, and metrics are synthetic. The simulator is not physiologically validated; synthetic distributions and dynamics do not represent real-world patient diversity or device error. The model has no external, prospective, subgroup, or clinical validation; chronological holdout results can still reflect synthetic generator assumptions. The prediction is not a medical device, diagnosis, treatment recommendation, or substitute for professional advice. Do not use for patient care.

## License

MIT. See [`LICENSE`](LICENSE). Dependencies retain their own licenses.
