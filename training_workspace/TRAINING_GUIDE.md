# Training Guide (Real Datasets)

This guide explains how the two demo models are trained using your datasets and how
the generated `.pkl` files are used by the runtime.

## Outputs

The training script produces two pickle files that the generated project loads at runtime:

- `activity_model.pkl` → used by `models/activity_model.py`
- `anomaly_model.pkl` → used by `models/anomaly_model.py`

These live in `training_workspace/output/` after training. Copy them into your
generated project `models/` folder.

## Activity model

**Purpose:** classify activity (`sleep`, `rest`, `walk`, `run`).

**Datasets used:**
- PAMAP2 (`PAMAP2_Dataset/Protocol/*.dat`)
- WISDM (`WISDM_ar_v1.1/WISDM_ar_v1.1_raw.txt`)

**Features:**
- Acceleration magnitude computed as:
  `max(abs(accel_x), abs(accel_y), abs(accel_z))`

**Algorithm:**
- Percentile thresholds over real acceleration magnitudes:
  - 25th percentile → `sleep`
  - 50th percentile → `rest`
  - 75th percentile → `walk`
  - Above → `run`

**Model artifact:**
```json
{"thresholds": [t1, t2, t3]}
```

## Anomaly model

**Purpose:** detect anomalies and report `tachycardia`, `bradycardia`, `fever`,
`heart_attack`, `cardiac_arrest`.

**Datasets used:**
- PAMAP2 (heart rate + optional temperature + acceleration magnitude)

**Features:**
- Heart rate from PAMAP2
- Temperature (if present in PAMAP2)
- Acceleration magnitude (same as above)

**Algorithm:**
- Tachycardia threshold = 90th percentile of heart rate
- Bradycardia threshold = 10th percentile of heart rate
- Fever threshold = 90th percentile of temperature (fallback to 38°C)
- Heart-attack threshold = 95th percentile of acceleration magnitude
- Cardiac arrest threshold = bradycardia − 5 bpm (clamped to >= 20)

**Model artifact:**
```json
{"thresholds": {"tachycardia": 120.0, ...}}
```

## Why this architecture

The runtime expects **simple threshold-based models** because it keeps the demo
lightweight and easy to replace. You can swap these `.pkl` files with models trained
from any other dataset as long as they expose the same threshold keys.

## Training command

```bash
python training_workspace/train_models.py --dataset-root "D:/Campus/.../dataset"
```

## Files used

- `training_workspace/train_models.py` → data loading + threshold training
- `models/activity_model.py` → loads `activity_model.pkl`
- `models/anomaly_model.py` → loads `anomaly_model.pkl`
