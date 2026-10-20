# GlucoTwin submission checklist

Status reflects the implementation and verification completed on 20 October 2026. “Pending” means team or organizer information is required, or a real-world artifact does not yet exist.

| Status | Requirement | Evidence / next step |
|---|---|---|
| Done | Synthetic historical EHR-style patient profiles | `data/patients.csv` contains 60 seeded fictional profiles with patient IDs, demographics, BMI, HbA1c, duration, and medication category. |
| Done | Timestamped synthetic sensor stream | `data/sensor_readings.csv` contains 120,960 simulated 15-minute readings with glucose, heart rate, activity, sleep, and time features. |
| Done | Prediction target documented as two hours ahead | Glucose at `t + 120 minutes`, aligned eight rows ahead in `train_model.py`. |
| Done | Reproducible ML pipeline | `generate_data.py` and `train_model.py`, seed 2026, local model artifact in `models/`. |
| Done | Chronological evaluation with leakage control | Later 20% timestamp holdout. A 120-minute purge ensures training targets precede the test cutoff. |
| Done | Baseline comparison and actual MAE | Model MAE 3.335 mg/dL; last-value baseline MAE 8.580 mg/dL. Synthetic-only values are in `data/metrics.json`. |
| Done | Patient profile and sensor history dashboard | Streamlit app displays the selected synthetic profile, simulated readings, forecast, and model metrics. |
| Done | Patient selection and stream-advance controls | AppTest verified selecting another patient and advancing by 15 minutes changes the state and prediction. |
| Done | Observed, simulated, and prediction distinction | No observed data are used. Profile, simulated readings, and model prediction have separate labels. |
| Done | Validation and automated tests | Timestamp and cadence validation; `pytest -q`: 4 passed. |
| Done | Startup check | Streamlit AppTest had no app exceptions; local server returned HTTP 200. |
| Done | Medical-use limits and synthetic-data labels | Present in app, README, architecture, and presentation. No clinical validation claims. |
| Done | Architecture PDF with readable architecture diagram | [docs/architecture.pdf](architecture.pdf). |
| Done | Professional 10-12 slide presentation | [docs/presentation.pdf](presentation.pdf), 11 slides. |
| Done | Timed presentation and demo script | [docs/demo_script.md](demo_script.md), 22-minute run of show. |
| Done | README includes required project, model, metrics, setup, architecture, presentation, license, and limitations | [README.md](../README.md). |
| Pending | Team member names | Replace `[Add team member names]` in README and title slide with supplied details. |
| Pending | College / institution | Replace `[Add institution]` with the team's supplied information. |
| Pending | Team contact details | Add only details supplied and approved for inclusion. No phone number or email has been invented. |
| Pending | Demo video | Record and upload the actual demonstration, then add its real link to README. |
| Pending | Competition-specific format and submission destination | Confirm current organizer instructions before preparing the final upload. |

## Evaluation record

- Model: `HistGradientBoostingRegressor`
- Training rows: 95,880
- Chronological test rows: 24,120
- Test cutoff: `2026-10-15T17:30:00+00:00`
- Model MAE: 3.335 mg/dL
- Last-value baseline MAE: 8.580 mg/dL
- Data and metrics are synthetic only. These values are not clinical performance.

## Screenshot status

The running dashboard was verified with Streamlit AppTest and actual state-transition values are used on the demo slide. A browser screenshot could not be captured during document preparation, so no screenshot or UI mock is included.
