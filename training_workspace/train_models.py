from __future__ import annotations

import math
import pickle
import random
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"


def _generate_activity_samples(count: int) -> list[float]:
    samples = []
    for _ in range(count):
        activity = random.choice(["sleep", "rest", "walk", "run"])
        if activity == "sleep":
            magnitude = random.uniform(0.0, 0.3)
        elif activity == "rest":
            magnitude = random.uniform(0.3, 1.0)
        elif activity == "walk":
            magnitude = random.uniform(1.0, 2.0)
        else:
            magnitude = random.uniform(2.0, 3.0)
        samples.append(magnitude)
    return samples


def _train_activity_thresholds(samples: list[float]) -> list[float]:
    samples = sorted(samples)
    if not samples:
        return [0.4, 1.2, 2.2]
    q1 = samples[int(len(samples) * 0.25)]
    q2 = samples[int(len(samples) * 0.5)]
    q3 = samples[int(len(samples) * 0.75)]
    return [round(q1, 2), round(q2, 2), round(q3, 2)]


def _generate_anomaly_samples(count: int) -> list[dict[str, float]]:
    samples = []
    for _ in range(count):
        heart_rate = random.uniform(40, 140)
        temperature = random.uniform(36.0, 39.5)
        accel = random.uniform(0.0, 4.0)
        samples.append(
            {
                "heart_rate": heart_rate,
                "body_temperature": temperature,
                "accel": accel,
            }
        )
    return samples


def _train_anomaly_thresholds(samples: list[dict[str, float]]) -> dict[str, float]:
    heart_rates = [sample["heart_rate"] for sample in samples]
    temps = [sample["body_temperature"] for sample in samples]
    accels = [sample["accel"] for sample in samples]
    heart_rates.sort()
    temps.sort()
    accels.sort()
    tachycardia = heart_rates[int(len(heart_rates) * 0.85)] if heart_rates else 120.0
    bradycardia = heart_rates[int(len(heart_rates) * 0.1)] if heart_rates else 50.0
    fever = temps[int(len(temps) * 0.85)] if temps else 38.0
    heart_attack = accels[int(len(accels) * 0.9)] if accels else 3.5
    cardiac_arrest = bradycardia - 5.0
    return {
        "tachycardia": round(tachycardia, 1),
        "bradycardia": round(bradycardia, 1),
        "fever": round(fever, 1),
        "heart_attack": round(heart_attack, 2),
        "cardiac_arrest": round(max(cardiac_arrest, 20.0), 1),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    activity_samples = _generate_activity_samples(500)
    activity_thresholds = _train_activity_thresholds(activity_samples)

    anomaly_samples = _generate_anomaly_samples(500)
    anomaly_thresholds = _train_anomaly_thresholds(anomaly_samples)

    activity_payload = {"thresholds": activity_thresholds}
    anomaly_payload = {"thresholds": anomaly_thresholds}

    (OUTPUT_DIR / "activity_model.pkl").write_bytes(pickle.dumps(activity_payload))
    (OUTPUT_DIR / "anomaly_model.pkl").write_bytes(pickle.dumps(anomaly_payload))

    print("Training complete.")
    print(f"Activity thresholds: {activity_thresholds}")
    print(f"Anomaly thresholds: {anomaly_thresholds}")
    print(f"Models saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    random.seed(42)
    main()
