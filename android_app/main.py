from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass
from typing import Callable

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


@dataclass
class SimulationConfig:
    name: str
    builder: Callable[[int], dict]


class SimulatorState:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self, target: Callable[[], None]) -> None:
        self.stop()
        self._stop_event.clear()
        self._thread = threading.Thread(target=target, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=1.0)
        self._thread = None

    def should_stop(self) -> bool:
        return self._stop_event.is_set()


class SimulatorApp(App):
    def build(self):
        self.title = "Altrus Simulator"
        self.state = SimulatorState()
        self.payload_label = Label(text="Payload will appear here.")

        root = BoxLayout(orientation="vertical", padding=12, spacing=8)

        ip_row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        ip_row.add_widget(Label(text="Host:", size_hint_x=None, width=60))
        self.host_input = TextInput(text="192.168.1.45", multiline=False)
        ip_row.add_widget(self.host_input)
        ip_row.add_widget(Label(text="Port:", size_hint_x=None, width=60))
        self.port_input = TextInput(text="5055", multiline=False, size_hint_x=None, width=90)
        ip_row.add_widget(self.port_input)
        root.add_widget(ip_row)

        buttons_layout = BoxLayout(orientation="vertical", spacing=6)
        for config in self._simulations():
            button = Button(text=config.name)
            button.bind(on_press=lambda _, c=config: self.start_simulation(c))
            buttons_layout.add_widget(button)
        stop_button = Button(text="Stop", background_color=(0.9, 0.2, 0.2, 1))
        stop_button.bind(on_press=lambda *_: self.stop_simulation())
        buttons_layout.add_widget(stop_button)
        root.add_widget(buttons_layout)

        root.add_widget(Label(text="Last payload:", size_hint_y=None, height=30))
        root.add_widget(self.payload_label)
        return root

    def _simulations(self) -> list[SimulationConfig]:
        return [
            SimulationConfig("Tachycardia", self._tachycardia_payload),
            SimulationConfig("Bradycardia", self._bradycardia_payload),
            SimulationConfig("Fever", self._fever_payload),
            SimulationConfig("Heart Attack", self._heart_attack_payload),
            SimulationConfig("Cardiac Arrest", self._cardiac_arrest_payload),
        ]

    def _tachycardia_payload(self, phase: int) -> dict:
        return self._base_payload(heart_rate=80.0 if phase == 0 else 140.0)

    def _bradycardia_payload(self, phase: int) -> dict:
        return self._base_payload(heart_rate=70.0 if phase == 0 else 40.0)

    def _fever_payload(self, phase: int) -> dict:
        temperature = 36.7 if phase == 0 else 39.2
        return self._base_payload(body_temperature=temperature)

    def _heart_attack_payload(self, phase: int) -> dict:
        accel = 0.3 if phase == 0 else 4.2
        return self._base_payload(accel_x=accel, accel_y=accel, accel_z=accel)

    def _cardiac_arrest_payload(self, phase: int) -> dict:
        return self._base_payload(heart_rate=75.0 if phase == 0 else 20.0)

    def _base_payload(
        self,
        heart_rate: float = 80.0,
        body_temperature: float = 36.7,
        accel_x: float = 0.3,
        accel_y: float = 0.2,
        accel_z: float = 0.1,
    ) -> dict:
        return {
            "heart_rate": heart_rate,
            "body_temperature": body_temperature,
            "accel_x": accel_x,
            "accel_y": accel_y,
            "accel_z": accel_z,
        }

    def _get_target(self) -> tuple[str, int]:
        host = self.host_input.text.strip() or "127.0.0.1"
        try:
            port = int(self.port_input.text.strip())
        except ValueError:
            port = 5055
        return host, port

    def start_simulation(self, config: SimulationConfig) -> None:
        host, port = self._get_target()

        def run_loop() -> None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start = time.time()
            while not self.state.should_stop():
                elapsed = time.time() - start
                phase = 0 if elapsed < 5 else 1
                payload = config.builder(phase)
                sock.sendto(json.dumps(payload).encode("utf-8"), (host, port))
                Clock.schedule_once(lambda *_: self._update_payload(payload))
                time.sleep(0.5)
            sock.close()

        self.state.start(run_loop)

    def stop_simulation(self) -> None:
        self.state.stop()

    def _update_payload(self, payload: dict) -> None:
        self.payload_label.text = json.dumps(payload, indent=2)


if __name__ == "__main__":
    SimulatorApp().run()
