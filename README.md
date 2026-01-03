# Altrus ML Model V2 CLI

This repository provides a Python CLI that scaffolds standalone wristband sensor fusion
projects for anomaly detection. The CLI gathers sensor and anomaly selections, then
creates a ready-to-edit project folder with configuration, simulation stubs, and model
hooks.

## Installation

```bash
pip install -e .
```

## Usage

```bash
altrus init
```

Follow the prompts to pick sensors, anomalies, target environments, and an output
location. A YAML configuration file will be generated so teams can update selections
later without rebuilding from scratch.
