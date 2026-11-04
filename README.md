# GlucoTwin — Digital Twin Challenge 2026

## Submission details

- **Project title:** GlucoTwin — Synthetic Two-Hour Glucose Digital Twin
- **Team members:** Gireesh Sadanand Patgar
- **College / institution:** The National Institute of Engineering, Mysuru
- **Team lead contact:** gireeshpatgar17@gmail.com
- **Presentation:** [docs/presentation.pdf](docs/presentation.pdf)
- **Architecture:** [docs/architecture.pdf](docs/architecture.pdf)

## Problem statement and healthcare use case

This proof of concept explores how a patient-specific digital twin interface could combine longitudinal context with simulated sensor data to estimate glucose two hours ahead. A future research workflow might help care teams inspect trends and evaluate forecasting concepts. This submission is an engineering demonstration only: its synthetic data, metrics, and predictions are not clinically validated and must not guide care.

## What it does

- Generates fictional patient profiles and timestamped 15-minute glucose, heart-rate, activity, and sleep features.
- Defines the target as sensor glucose at `t + 120 minutes` (eight 15-minute steps).
- Trains on earlier timestamps and evaluates on later timestamps; reports MAE beside a last-value baseline.
- Shows a patient profile, virtual stream state, recent history, prediction and actual run metrics in Streamlit.
- Advances the simulated stream in 15-minute increments. Labels EHR profile, simulated sensor values, and prediction separately.
- Uses no observed patient data. Every profile and sensor value is synthetic or simulated.

## Competition requirements coverage

| Requirement | Implementation and evidence |
|---|---|
| Synthetic historical EHR-style profiles | `data/patients.csv`: patient ID, age, sex, BMI, HbA1c, duration, and medication category. |
| Timestamped sensor stream | `data/sensor_readings.csv`: glucose, heart rate, activity, sleep, and time features at 15-minute cadence. |
| Clear two-hour prediction target | `train_model.py`: glucose at timestamp `t + 120 minutes`, aligned eight rows ahead. |
| Reproducible pipeline and baseline | Seeded generator, scikit-learn model, chronological holdout, two-hour purge, and current-glucose persistence baseline. |
| Evaluation metrics | Actual synthetic run is documented below and in `data/metrics.json`. |
| Interactive dashboard | `app.py`: choose patient, inspect profile and history, advance sensor stream, view forecast and metrics. |
| Data and prediction labels | Dashboard identifies profile as synthetic EHR, readings as simulated, and forecast as a prediction. No observed values are presented. |
| Input validation and automated tests | Timestamp/cadence checks in training pipeline; `pytest -q` currently passes four tests. |
| Medical-use limitations | Synthetic-only, non-clinical status appears in the app and this README. |
| Submission documents | Architecture, 11-slide presentation, and timed demo script are linked above. |

## Technical stack and model

Python, Streamlit, pandas, NumPy, scikit-learn, Plotly, pytest, and joblib. The preferred model is `HistGradientBoostingRegressor`; if scikit-learn is unavailable, the training script uses a standardized NumPy ridge fallback and Python pickle so offline generation and evaluation remain possible. Install the listed dependencies to reproduce the preferred model. No paid APIs, external health services, cloud database, or Docker are used.

## Evaluation results

The verified scikit-learn run used 60 profiles and 120,960 simulated 15-minute readings. The chronological split trained on 95,880 rows, evaluated on 24,120 later rows, and used cutoff `2026-10-15T17:30:00+00:00`. A two-hour purge excludes training rows whose target reaches the test period. `HistGradientBoostingRegressor` achieved **3.335 mg/dL MAE**; the current-glucose persistence baseline achieved **8.580 mg/dL MAE**. These results describe only the deterministic synthetic generator and are not clinical performance. Full run details are saved in [`data/metrics.json`](data/metrics.json) and `models/metrics.json`.

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

The checked-in CSVs and `models/glucose_model.joblib` are generated using seed 2026. Re-run the commands above to regenerate. If scikit-learn/joblib are unavailable, `train_model.py` uses a NumPy ridge fallback and pickle; the Streamlit runtime still requires Streamlit and Plotly. Verified with Python 3.12: all four pytest tests pass, the Streamlit app returns HTTP 200, and Streamlit AppTest confirms patient selection and stream advance change the profile, current sensor state, and prediction. A real browser screenshot was not available during document preparation, so the presentation uses verified interaction values instead of a screenshot.

## Architecture

`generate_data.py` creates synthetic EHR and sensor CSVs. `train_model.py` aligns each row with the reading eight intervals (120 minutes) later, joins patient features, and uses an 80/20 chronological pooled-time holdout with a 120-minute purge. It compares against current-glucose persistence and stores the model and metrics. Prediction features include the selected patient's current simulated reading and static synthetic profile only; the dashboard does not pass later sensor rows to the predictor. `app.py` advances the cursor by 15 minutes and recomputes the prediction from the new current row. See [`docs/architecture.pdf`](docs/architecture.pdf).

## Limitations and medical-use notice

All people, records, sensor values, and metrics are synthetic. The simulator is not physiologically validated; synthetic distributions and dynamics do not represent real-world patient diversity or device error. The model has no external, prospective, subgroup, or clinical validation; chronological holdout results can still reflect synthetic generator assumptions. The prediction is not a medical device, diagnosis, treatment recommendation, or substitute for professional advice. Do not use for patient care.

## License

MIT. See [`LICENSE`](LICENSE). Dependencies retain their own licenses.
