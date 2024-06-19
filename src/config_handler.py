import json
from dataclasses import dataclass
from inspect import signature
from typing import Any, Literal

from dataclasses_json import dataclass_json

from src.filepath import CONFIG_PATH

# Fill data currently not in the config file,
# need at least all that config has
NEEDED_DATA = {
    "name": "",
    "save_path": "",
    "daily_hours": 8.0,
    "weekly_hours": 40.0,
    "country": "US",
    "subdiv": None,
    "workdays": [0, 1, 2, 3, 4],  # 0-6, 0=Monday, 6=Sunday
    "plot_pause": True,
}
CONFIG_NAMES = Literal[
    "name", "save_path", "country", "subdiv", "daily_hours", "weekly_hours", "workdays", "plot_pause"
]


@dataclass
@dataclass_json
class Config:
    name: str
    save_path: str
    daily_hours: float
    weekly_hours: float
    country: str
    subdiv: str | None
    workdays: list[int]
    plot_pause: bool

    @classmethod
    def from_kwargs(cls, **kwargs):
        cls_fields = set(signature(cls).parameters)

        class_args, other_args = {}, {}
        for name, val in kwargs.items():
            if name in cls_fields:
                class_args[name] = val
                continue
            other_args[name] = val

        c = cls(**class_args)
        for new_name, new_val in other_args.items():
            setattr(c, new_name, new_val)
        return c

    def __getitem__(self, item):
        return getattr(self, item)


class ConfigHandler:
    def __init__(self):
        """Class for managing configuration file and settings ."""
        self.config = self._get_config()

    def _get_config(self):
        config_file = self.read_config_file()
        return Config.from_kwargs(**config_file)

    def read_config_file(self) -> dict:
        if not CONFIG_PATH.exists():
            return NEEDED_DATA
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
        for d in NEEDED_DATA.items():
            if d[0] not in config:
                config[d[0]] = d[1]
        return config

    def write_config_file(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as write_file:
            # pylint: disable=no-member
            json.dump(self.config.to_dict(), write_file)  # type: ignore

    def set_config_value(self, key: CONFIG_NAMES, value: Any, write: bool = True):
        setattr(self.config, key, value)
        if not write:
            return
        self.write_config_file()


CONFIG_HANDLER = ConfigHandler()
