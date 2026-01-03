from __future__ import annotations

import argparse
from pathlib import Path

from altrus_cli.generator import ProjectConfig, create_project

PREDEFINED_SENSORS = [
    "accelerometer",
    "gyroscope",
    "ppg",
    "ecg",
    "temperature",
    "spo2",
    "eda",
    "barometer",
]

PREDEFINED_ANOMALIES = [
    "fall_detection",
    "arrhythmia",
    "stress_spike",
    "overexertion",
    "sleep_disruption",
]

ENVIRONMENTS = [
    "raspberry_pi",
    "linux",
    "windows",
]


def _prompt_text(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default:
            return default
        if value:
            return value
        print("Please enter a value.")


def _prompt_multi_select(title: str, options: list[str]) -> list[str]:
    print(f"\n{title}")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option}")
    print("  c. Add custom entries")
    print("  a. Select all")

    selections: list[str] = []
    while not selections:
        raw = input("Enter selection numbers (comma-separated): ").strip().lower()
        if raw == "a":
            return options.copy()

        entries = [entry.strip() for entry in raw.split(",") if entry.strip()]
        custom_requested = "c" in entries
        selected_indices = [entry for entry in entries if entry.isdigit()]

        for entry in selected_indices:
            idx = int(entry)
            if 1 <= idx <= len(options):
                selections.append(options[idx - 1])

        if custom_requested:
            custom_raw = _prompt_text("Enter custom values (comma-separated)")
            custom_values = [value.strip() for value in custom_raw.split(",") if value.strip()]
            selections.extend(custom_values)

        selections = list(dict.fromkeys(selections))
        if not selections:
            print("Please make at least one selection.")

    return selections


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a wristband sensor fusion project scaffold.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a new project scaffold")
    init_parser.add_argument("--name", help="Project name")
    init_parser.add_argument(
        "--output",
        help="Directory to create the project in",
        default=str(Path.cwd()),
    )

    return parser.parse_args()


def _run_init(args: argparse.Namespace) -> None:
    name = args.name or _prompt_text("Project name", default="wristband_project")
    output_dir = Path(args.output).expanduser().resolve()

    sensors = _prompt_multi_select("Select wristband sensors", PREDEFINED_SENSORS)
    anomalies = _prompt_multi_select("Select anomalies to detect", PREDEFINED_ANOMALIES)
    environments = _prompt_multi_select("Select target environments", ENVIRONMENTS)

    config = ProjectConfig(
        name=name,
        sensors=sensors,
        anomalies=anomalies,
        environments=environments,
    )

    project_path = create_project(config, output_dir)
    print(f"\nProject created at: {project_path}")


def main() -> None:
    args = _parse_args()
    if args.command == "init":
        _run_init(args)


if __name__ == "__main__":
    main()
