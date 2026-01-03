from __future__ import annotations

import argparse
import csv
import math
import pickle
from pathlib import Path
from typing import Iterable

OUTPUT_DIR = Path(__file__).parent / "output"

PAMAP2_ACTIVITY_MAP = {
    1: "sleep",  # lying
    2: "rest",  # sitting
    3: "rest",  # standing
    4: "walk",  # walking
    5: "run",  # running
    6: "walk",  # cycling
    7: "walk",  # nordic walking
    9: "rest",  # watching TV
    10: "rest",  # computer work
    11: "rest",  # car driving
    12: "walk",  # ascending stairs
    13: "walk",  # descending stairs
    16: "walk",  # vacuum cleaning
    17: "walk",  # ironing
    18: "walk",  # folding laundry
    19: "walk",  # house cleaning
    20: "run",  # playing soccer
}

WISDM_ACTIVITY_MAP = {
    "Walking": "walk",
    "Jogging": "run",
    "Sitting": "rest",
    "Standing": "rest",
    "LyingDown": "sleep",
}

ACTIVITY_ORDER = ["sleep", "rest", "walk", "run"]


def _percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = int(len(values) * ratio)
    index = min(max(index, 0), len(values) - 1)
    return values[index]


def _safe_float(value: str) -> float | None:
    try:
        number = float(value)
    except ValueError:
        return None
    if math.isnan(number):
        return None
    return number


def _accel_magnitude(x: float | None, y: float | None, z: float | None) -> float | None:
    if x is None or y is None or z is None:
        return None
    return max(abs(x), abs(y), abs(z))


def _load_pamap2(protocol_dir: Path) -> tuple[list[tuple[float, str]], list[float], list[float]]:
    labeled_magnitudes: list[tuple[float, str]] = []
    heart_rates: list[float] = []
    temperatures: list[float] = []

    for path in sorted(protocol_dir.glob("*.dat")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.strip().split()
                if len(parts) < 7:
                    continue
                activity_id = int(float(parts[1]))
                mapped = PAMAP2_ACTIVITY_MAP.get(activity_id)
                if not mapped:
                    continue
                heart_rate = _safe_float(parts[2])
                temp = _safe_float(parts[3])
                accel = _accel_magnitude(
                    _safe_float(parts[4]),
                    _safe_float(parts[5]),
                    _safe_float(parts[6]),
                )
                if accel is not None:
                    labeled_magnitudes.append((accel, mapped))
                if heart_rate is not None:
                    heart_rates.append(heart_rate)
                if temp is not None:
                    temperatures.append(temp)
    return labeled_magnitudes, heart_rates, temperatures


def _load_wisdm(raw_path: Path) -> list[tuple[float, str]]:
    labeled_magnitudes: list[tuple[float, str]] = []
    with raw_path.open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 6:
                continue
            activity = row[1].strip()
            mapped = WISDM_ACTIVITY_MAP.get(activity)
            if not mapped:
                continue
            x = _safe_float(row[3])
            y = _safe_float(row[4])
            z = _safe_float(row[5].rstrip(";"))
            accel = _accel_magnitude(x, y, z)
            if accel is not None:
                labeled_magnitudes.append((accel, mapped))
    return labeled_magnitudes


def _train_activity_thresholds(magnitudes: list[float]) -> list[float]:
    if not magnitudes:
        return [0.4, 1.2, 2.2]
    return [
        round(_percentile(magnitudes, 0.25), 2),
        round(_percentile(magnitudes, 0.5), 2),
        round(_percentile(magnitudes, 0.75), 2),
    ]


def _predict_activity(magnitude: float, thresholds: list[float]) -> str:
    if magnitude <= thresholds[0]:
        return "sleep"
    if magnitude <= thresholds[1]:
        return "rest"
    if magnitude <= thresholds[2]:
        return "walk"
    return "run"


def _evaluate_activity(labeled: list[tuple[float, str]], thresholds: list[float]) -> dict:
    if not labeled:
        return {"accuracy": 0.0, "total": 0, "correct": 0}
    correct = 0
    total = 0
    per_class = {label: {"correct": 0, "total": 0} for label in ACTIVITY_ORDER}
    for magnitude, label in labeled:
        prediction = _predict_activity(magnitude, thresholds)
        total += 1
        per_class[label]["total"] += 1
        if prediction == label:
            correct += 1
            per_class[label]["correct"] += 1
    return {
        "accuracy": correct / total if total else 0.0,
        "total": total,
        "correct": correct,
        "per_class": per_class,
    }


def _train_anomaly_thresholds(
    heart_rates: list[float],
    temperatures: list[float],
    accel_magnitudes: list[float],
) -> dict[str, float]:
    tachycardia = _percentile(heart_rates, 0.9) if heart_rates else 120.0
    bradycardia = _percentile(heart_rates, 0.1) if heart_rates else 50.0
    fever = _percentile(temperatures, 0.9) if temperatures else 38.0
    heart_attack = _percentile(accel_magnitudes, 0.95) if accel_magnitudes else 3.5
    cardiac_arrest = max(bradycardia - 5.0, 20.0)
    return {
        "tachycardia": round(tachycardia, 1),
        "bradycardia": round(bradycardia, 1),
        "fever": round(fever, 1),
        "heart_attack": round(heart_attack, 2),
        "cardiac_arrest": round(cardiac_arrest, 1),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train demo activity/anomaly thresholds from real datasets.",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True,
        help="Path to the dataset root containing PAMAP2/WISDM folders.",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Print activity classification accuracy from the training data.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    dataset_root = args.dataset_root

    pamap2_dir = dataset_root / "PAMAP2_Dataset" / "Protocol"
    wisdm_path = dataset_root / "WISDM_ar_v1.1" / "WISDM_ar_v1.1_raw.txt"

    labeled_magnitudes: list[tuple[float, str]] = []
    heart_rates: list[float] = []
    temperatures: list[float] = []

    if pamap2_dir.exists():
        pamap2_labeled, pamap2_hr, pamap2_temp = _load_pamap2(pamap2_dir)
        labeled_magnitudes.extend(pamap2_labeled)
        heart_rates.extend(pamap2_hr)
        temperatures.extend(pamap2_temp)

    if wisdm_path.exists():
        labeled_magnitudes.extend(_load_wisdm(wisdm_path))

    magnitudes = [value for value, _ in labeled_magnitudes]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    activity_thresholds = _train_activity_thresholds(magnitudes)
    anomaly_thresholds = _train_anomaly_thresholds(heart_rates, temperatures, magnitudes)

    activity_payload = {"thresholds": activity_thresholds}
    anomaly_payload = {"thresholds": anomaly_thresholds}

    (OUTPUT_DIR / "activity_model.pkl").write_bytes(pickle.dumps(activity_payload))
    (OUTPUT_DIR / "anomaly_model.pkl").write_bytes(pickle.dumps(anomaly_payload))

    print("Training complete.")
    print(f"Activity thresholds: {activity_thresholds}")
    print(f"Anomaly thresholds: {anomaly_thresholds}")
    print(f"Models saved to: {OUTPUT_DIR}")

    if args.evaluate:
        results = _evaluate_activity(labeled_magnitudes, activity_thresholds)
        print(f"Activity accuracy: {results['accuracy']:.3f} ({results['correct']}/{results['total']})")
        for label in ACTIVITY_ORDER:
            stats = results["per_class"][label]
            if stats["total"]:
                rate = stats["correct"] / stats["total"]
                print(f"  {label}: {rate:.3f} ({stats['correct']}/{stats['total']})")


if __name__ == "__main__":
    main()
