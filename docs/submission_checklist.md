# Digital Twin Challenge submission checklist

- [x] Local Python and Streamlit proof of concept source
- [x] Deterministic synthetic EHR and sensor generator
- [x] Target explicitly defined as glucose at t + 120 minutes
- [x] Chronological holdout and last-value baseline metric
- [x] Patient selection and 15-minute stream advance control
- [x] Visual distinction among fictional profile, simulated values, and predictions
- [x] Input checks and automated test source
- [x] Medical-use limitations and synthetic-data labels
- [x] Architecture PDF, presentation PDF, and demo script
- [ ] Replace team, college, and contact placeholders with supplied details
- [ ] Record and add an actual demo video link
- [x] Install declared dependencies into local `.venv` and train the scikit-learn model
- [x] Run `pytest -q` (4 passed)
- [x] Launch Streamlit locally; HTTP startup check returned 200
- [x] Advance the dashboard stream and verify current sensor value and forecast update
- [ ] Confirm event-specific submission format and upload destination with organizers
