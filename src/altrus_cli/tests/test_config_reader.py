from __future__ import annotations

from pathlib import Path

from altrus_cli.infrastructure.config_yaml import YamlConfigReader


def test_yaml_config_reader(tmp_path: Path):
    config_path = tmp_path / "wristband_config.yaml"
    config_path.write_text(
        """activities:\n"
        "  - sleep\n"
        "  - walk\n"
        "anomalies:\n"
        "  - tachycardia\n"
        "  - fever\n",
        encoding="utf-8",
    )

    reader = YamlConfigReader(config_path)
    config = reader.load()

    assert config.activities == ["sleep", "walk"]
    assert config.anomalies == ["tachycardia", "fever"]
