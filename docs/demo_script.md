# GlucoTwin demo script (about 3 minutes)

1. **Set context (20 sec).** “GlucoTwin is a local, synthetic-data proof of concept for a two-hour glucose forecast. It is not a clinical tool.”
2. **Show profile (35 sec).** Select a synthetic patient. Point out age, BMI, HbA1c and duration are fictional EHR-style attributes.
3. **Show stream (35 sec).** Identify glucose, heart rate, activity and sleep as simulated 15-minute readings. The displayed timestamp is the stream cursor.
4. **Advance state (30 sec).** Click “Advance sensor stream by 15 minutes.” Explain this moves the virtual patient stream one record; the current sensor value is not the future prediction.
5. **Explain forecast (40 sec).** Point to the diamond and forecast timestamp, which is exactly two hours after the current cursor. Emphasize it is a model prediction.
6. **Explain evaluation (35 sec).** Read model MAE and last-value baseline MAE from the generated held-out synthetic metrics. Describe the chronological time split. Do not claim clinical validation or generalization.
7. **Close (15 sec).** State next steps: validate with appropriate governance and consented real-world data before any clinical use. Do not present this prototype as ready for care.

## Capture checklist

- Record the real running app and actual displayed metrics; do not add edited performance claims.
- Keep the synthetic-data and medical-use notice visible in the recording.
- Add the real video URL to README only after it exists and is accessible.
