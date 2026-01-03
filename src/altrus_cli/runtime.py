from __future__ import annotations

import json
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class RuntimeConfig:
    activities: list[str]
    anomalies: list[str]


DEFAULT_ACTIVITIES = ["sleep", "rest", "walk", "run"]
DEFAULT_ANOMALIES = [
    "tachycardia",
    "bradycardia",
    "fever",
    "heart_attack",
    "cardiac_arrest",
]


def _format_payload(payload: dict) -> str:
    parts = []
    if "heart_rate" in payload:
        parts.append(f"hr={payload['heart_rate']}")
    if "body_temperature" in payload:
        parts.append(f"temp={payload['body_temperature']}")
    if all(key in payload for key in ("accel_x", "accel_y", "accel_z")):
        parts.append(
            "acc=({:.2f},{:.2f},{:.2f})".format(
                payload["accel_x"], payload["accel_y"], payload["accel_z"]
            )
        )
    if not parts:
        parts.append(f"payload={payload}")
    return " ".join(parts)


def _load_config(path: Path) -> RuntimeConfig:
    if not path.exists():
        return RuntimeConfig(activities=DEFAULT_ACTIVITIES)

    activities: list[str] = []
    anomalies: list[str] = []
    current_key: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.startswith("-") and stripped.endswith(":"):
            current_key = stripped[:-1].strip()
            continue
        if stripped.startswith("-") and current_key == "activities":
            activities.append(stripped.lstrip("-").strip())
        if stripped.startswith("-") and current_key == "anomalies":
            anomalies.append(stripped.lstrip("-").strip())

    return RuntimeConfig(
        activities=activities or DEFAULT_ACTIVITIES,
        anomalies=anomalies or DEFAULT_ANOMALIES,
    )


def _run_with_udp(host: str, port: int, handle_payload: callable) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        sock.settimeout(1.0)
        while True:
            try:
                data, _ = sock.recvfrom(4096)
            except socket.timeout:
                continue
            handle_payload(data)


def _run_with_tcp(host: str, port: int, handle_payload: callable) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(1)
        sock.settimeout(1.0)
        while True:
            try:
                conn, _ = sock.accept()
            except socket.timeout:
                continue
            with conn:
                conn.settimeout(1.0)
                buffer = b""
                while True:
                    try:
                        chunk = conn.recv(4096)
                    except socket.timeout:
                        continue
                    if not chunk:
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        handle_payload(line)


def run_scanner(
    project_root: Path,
    protocol: str,
    host: str,
    port: int,
    output_interval: float,
) -> None:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from pipelines.inference import run_inference

    config = _load_config(project_root / "config" / "wristband_config.yaml")

    last_output = 0.0

    def handle_payload(raw: bytes) -> None:
        nonlocal last_output
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return
        if not isinstance(payload, dict):
            return
        prediction = run_inference(payload, config.activities, config.anomalies)
        now = time.time()
        if now - last_output >= output_interval:
            status = "ANOMALY" if prediction["anomaly"] else "normal"
            summary = _format_payload(payload)
            print(
                f"{summary} -> {status} "
                f"activity={prediction['activity']} "
                f"type={prediction['anomaly_type']} (score={prediction['score']})"
            )
            last_output = now

    print(
        f"Listening for {protocol.upper()} sensor data on {host}:{port}. "
        "Press Ctrl+C to stop."
    )
    try:
        if protocol == "udp":
            _run_with_udp(host, port, handle_payload)
        else:
            _run_with_tcp(host, port, handle_payload)
    except KeyboardInterrupt:
        print("\nScanner stopped.")
