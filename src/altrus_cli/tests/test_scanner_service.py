from __future__ import annotations

import json

from altrus_cli.domain.scanner_service import ScannerService
from altrus_cli.ports.interfaces import RuntimeConfig


class FakeConfig:
    def load(self) -> RuntimeConfig:
        return RuntimeConfig(["sleep"], ["tachycardia"])


class FakeReceiver:
    def __init__(self, payloads: list[dict]):
        self.payloads = payloads

    def iter_messages(self):
        for payload in self.payloads:
            yield json.dumps(payload).encode("utf-8")


class FakePredictor:
    def predict(self, payload: dict, activities: list[str], anomalies: list[str]) -> dict:
        return {
            "activity": activities[0],
            "anomaly": payload.get("heart_rate", 0) > 100,
            "anomaly_type": "tachycardia" if payload.get("heart_rate", 0) > 100 else "normal",
            "score": 1.0,
        }


class FakeFormatter:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def format(self, payload: dict, prediction: dict) -> str:
        message = f"{payload['heart_rate']}:{prediction['anomaly_type']}"
        self.messages.append(message)
        return message


def test_scanner_service_emits_messages(capsys):
    receiver = FakeReceiver([
        {"heart_rate": 90},
        {"heart_rate": 120},
    ])
    formatter = FakeFormatter()
    service = ScannerService(FakeConfig(), receiver, FakePredictor(), formatter)

    service.run()

    captured = capsys.readouterr()
    assert "90:normal" in captured.out
    assert "120:tachycardia" in captured.out
    assert formatter.messages == ["90:normal", "120:tachycardia"]
