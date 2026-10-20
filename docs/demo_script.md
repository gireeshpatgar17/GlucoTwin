# GlucoTwin presentation and demo script

**Run time:** 22 minutes, including the live walkthrough and a short close. The script follows the 11-slide deck. If the event format requires a shorter slot, reduce the demo to patient selection and one stream advance.

## Before presenting

- Start the app from the project root with `streamlit run app.py`.
- Keep the synthetic-data warning visible. Do not describe any output as a clinical result.
- Confirm the README and `data/metrics.json` have the current evaluation. The current model is `HistGradientBoostingRegressor`, trained on 95,880 rows and evaluated on 24,120 later rows.
- The dashboard interactions were verified with Streamlit AppTest. No browser screenshot is included in the slide deck because a real screenshot could not be captured during document preparation. Do not substitute a mock screenshot.
- Replace team, institution, and contact placeholders only with details supplied by the team. Add a video link only after a real recording has been uploaded.

## Timed talk track

### 0:00-1:30 | Slide 1 - Opening (1 min 30 sec)

“Hello, we are presenting GlucoTwin, a local proof of concept for a digital twin that forecasts synthetic glucose two hours ahead. The project combines synthetic EHR-style profile context with a simulated sensor stream, then shows the current virtual patient state and the model estimate in a Streamlit dashboard. All displayed people and readings are generated. This is an engineering demonstration, not a clinical tool. Our team, college, and contact information will be added here after confirmation.”

### 1:30-3:30 | Slide 2 - The problem (2 min)

“The task we chose is narrowly defined: given the current sensor and profile state, estimate glucose 120 minutes later. The stream is sampled every 15 minutes, so the target is the eighth subsequent reading. We chose this horizon because it makes the timing explicit and gives us a measurable supervised-learning target. The interface keeps the current simulated value separate from the estimate and labels the target time. We are not claiming this forecast is accurate for a person with diabetes.”

Point at the timeline on the slide. Say: “At time t, the model receives the current row. The label for training comes from t plus eight intervals. At inference, the dashboard shows a prediction at t plus two hours.”

### 3:30-5:10 | Slide 3 - Healthcare use case (1 min 40 sec)

“A possible research question is whether profile context and a streaming sensor view can be presented together in a way that helps a reviewer explore forecasts. In this prototype, the profile includes synthetic age, BMI, HbA1c, diabetes duration, and medication category. The simulated stream includes glucose, heart rate, activity, sleep, and time-of-day features. A reviewer can select a profile and advance the virtual clock. Any real healthcare study would need appropriate governance, consent, data quality checks, and validation before making claims about clinical use.”

### 5:10-6:40 | Slide 4 - Existing gap (1 min 30 sec)

“The gap we address is an engineering one in this demonstration: prediction horizon and evaluation timing should be clear, future rows should not enter prediction inputs, and simulated data should be visibly separated from predictions. This slide lists those safeguards and the corresponding failure modes. It is not a market survey or a claim that existing clinical systems lack these capabilities. Our result is a small, reproducible baseline that can be inspected and rerun.”

### 6:40-8:50 | Slide 5 - Architecture (2 min 10 sec)

Trace the diagram from left to right. “The generator creates two local synthetic sources: patient profiles and timestamped sensor readings. Preprocessing sorts each patient stream, checks the 15-minute cadence, and aligns glucose eight rows forward for the label. Feature generation uses the current sensor row plus static profile fields. The trained HistGradientBoosting model returns a local estimate. The virtual patient state tracks the selected patient and current stream position. The dashboard shows profile, history, prediction, and evaluation metrics. Its advance control moves the simulated clock by one record and recomputes the prediction.”

“The feedback arrow changes only the simulation cursor. It does not represent a physical device or a real patient's sensor.”

### 8:50-10:50 | Slide 6 - Data (2 min)

“The current seed produces 60 fictional profiles and 120,960 readings. The readings are spaced every 15 minutes over 21 simulated days per profile. Profile features include age, sex, BMI, HbA1c, duration, and medication category. Sensor features include glucose, heart rate, activity, sleep flag, and cyclic time. These are generated values, not de-identified or observed records. The same seed regenerates the same sample data.”

### 10:50-12:50 | Slide 7 - Target and leakage controls (2 min)

“The label is glucose at t plus 120 minutes. The input columns are the current glucose, heart rate, activity, sleep, time-of-day, and selected profile fields. At inference, `forecast.py` constructs only those named features from the current row and the profile. It does not receive subsequent sensor rows. For evaluation, we hold out later timestamps. We also purge training rows whose target time would reach the test cutoff, which prevents the two-hour labels near the boundary from crossing into the test period.”

“We checked this boundary in the automated tests. This reduces leakage risk in the temporal split, but it does not make the synthetic evaluation clinically meaningful.”

### 12:50-14:20 | Slide 8 - Model and baseline (1 min 30 sec)

“With scikit-learn installed, the training script fits HistGradientBoostingRegressor. We compare it with a persistence baseline that predicts the current glucose unchanged at the two-hour horizon. The fallback NumPy ridge model exists for offline generation, but the reported run and checked-in model use the scikit-learn estimator. The exact model choice and metrics are stored alongside the artifact. We did not conduct clinical calibration or claim a tuned production model.”

### 14:20-16:20 | Slide 9 - Evaluation (2 min)

“This run used 95,880 training rows and 24,120 test rows. The cutoff was 15 October 2026 at 17:30 UTC, with a two-hour purge between training targets and the later test period. Model MAE was 3.335 mg/dL; persistence baseline MAE was 8.580 mg/dL on the same held-out rows. These are measurements from this deterministic synthetic generator. They show the model fits this generated process better than persistence in this split. They do not establish real-world accuracy, safety, fairness, benefit, or generalization.”

### 16:20-20:10 | Slide 10 - Live dashboard demonstration (3 min 50 sec)

1. Open the running local Streamlit app. Point to the synthetic-data and medical-use warning.
2. Select `SYN-001`. Identify the profile panel as synthetic EHR-style data and the current glucose, heart rate, activity, sleep, and timestamp as simulated sensor values.
3. Read the displayed current state. In the verified run, the initial cursor was `2026-10-19 00:00 UTC`, current glucose was `95 mg/dL`, and the prediction was `95.0 mg/dL` at the two-hour target time.
4. Click **Advance sensor stream by 15 minutes** once. In the verified run, the cursor moved to `00:15 UTC`, current glucose changed to `97 mg/dL`, and the prediction changed to `95.2 mg/dL`.
5. Select `SYN-002`. In the verified AppTest run at the aligned cursor, current glucose was `129 mg/dL` and the prediction was `131.2 mg/dL`. The selected profile, reading, and prediction all changed.
6. Point at the chart. Explain that the line contains simulated readings through the current cursor, while the diamond marks a prediction at current time plus two hours. There is no observed future value shown.
7. Read the model and persistence MAE from the evaluation section, and repeat that both metrics are synthetic-only.

If the app cannot be reached during the live session, use the actual transition values on this slide. Do not imply a screenshot is present or show a fabricated screen.

### 20:10-21:30 | Slide 11 - Limitations and next work (1 min 20 sec)

“The current virtual patient physiology is simplified and generated. The model has not been validated with external, prospective, subgroup, or clinical data. Before any clinical research claim, the team would need governance and consent, appropriate data, external and subgroup validation, safety analysis, and review of whether this workflow helps users. The real demo video is still pending recording and upload. Team and institution details are also pending confirmation.”

### 21:30-22:00 | Close and questions (30 sec)

“GlucoTwin demonstrates a reproducible path from synthetic profile and sensor streams to a leakage-aware two-hour forecast and an interactive local dashboard. The code, setup, measured synthetic evaluation, architecture, and presentation are linked in the README. Thank you. We welcome questions about the target definition, time split, implementation, or limitations.”

## Values to keep consistent

| Item | Verified value |
|---|---:|
| Sample profiles | 60 synthetic profiles |
| Simulated readings | 120,960 at 15-minute cadence |
| Target horizon | 120 minutes (eight samples) |
| Train / test rows | 95,880 / 24,120 |
| Chronological cutoff | 2026-10-15 17:30 UTC |
| Model MAE | 3.335 mg/dL |
| Persistence baseline MAE | 8.580 mg/dL |
| Video | Pending real recording and upload |
