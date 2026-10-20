# Synthetic sample data

These generated files contain fictional data only. `patients.csv` has synthetic EHR-style profiles. `sensor_readings.csv` has simulated 15-minute readings and derived features; every row has `data_status=simulated`. `metrics.json` records the model and chronological evaluation produced by `train_model.py`.

Regenerate from the project root with `python generate_data.py` using seed 2026. No real patient records are included.
