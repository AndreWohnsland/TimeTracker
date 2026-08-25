from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from src.config_handler import ConfigHandler


def test_config_survives_write_read_roundtrip(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    with patch("src.config_handler.CONFIG_PATH", config_file):
        handler = ConfigHandler()
        handler.set_config_value("name", "Alice")
        handler.set_config_value("work_hours", 32.5)
        handler.set_config_value("workdays", [0, 1, 2, 3])

        reloaded = ConfigHandler()

    assert reloaded.config.name == "Alice"
    assert reloaded.config.work_hours == 32.5
    assert reloaded.config.workdays == [0, 1, 2, 3]
    assert asdict(reloaded.config) == asdict(handler.config)
