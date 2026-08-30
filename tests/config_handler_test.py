from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from stempeluhr.config_handler import ConfigHandler


def test_config_survives_write_read_roundtrip(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    with patch("stempeluhr.config_handler.CONFIG_PATH", config_file):
        handler = ConfigHandler()
        handler.set_config_value("name", "Alice")
        handler.set_config_value("country", "DE")
        handler.set_config_value("project_names", ["Alpha", "Beta"])

        reloaded = ConfigHandler()

    assert reloaded.config.name == "Alice"
    assert reloaded.config.country == "DE"
    assert reloaded.config.project_names == ["Alpha", "Beta"]
    assert asdict(reloaded.config) == asdict(handler.config)
