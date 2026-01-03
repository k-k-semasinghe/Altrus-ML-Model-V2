# Training Workspace

This folder is a temporary workspace for training and exporting demo models. You can
safely delete it after you generate the `.pkl` files you need.

## Run training

```bash
python training_workspace/train_models.py --dataset-root "D:/path/to/dataset"
```

To include basic activity accuracy metrics:

```bash
python training_workspace/train_models.py --dataset-root "D:/path/to/dataset" --evaluate
```

The script writes the models to:

```
training_workspace/output/activity_model.pkl
training_workspace/output/anomaly_model.pkl
```

Copy those files into your generated project `models/` directory to use them.

## Supported datasets

The trainer reads:

- `PAMAP2_Dataset/Protocol/*.dat` (activity + heart rate + temperature)
- `WISDM_ar_v1.1/WISDM_ar_v1.1_raw.txt` (activity accelerometer)

If a dataset is missing, the script will fall back to default thresholds for the
missing signals.
