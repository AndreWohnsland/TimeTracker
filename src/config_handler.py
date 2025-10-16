import datetime
import json
from dataclasses import dataclass
from inspect import signature
from typing import Any, Literal

import holidays
from dataclasses_json import dataclass_json

from src.filepath import CONFIG_PATH

# Fill data currently not in the config file,
# need at least all that config has
NEEDED_DATA = {
    "name": "",
    "save_path": "",
    "work_hours": 40.0,
    "use_hours_per_week": True,
    "country": "US",
    "subdiv": None,
    "workdays": [0, 1, 2, 3, 4],  # 0-6, 0=Monday, 6=Sunday
    "different_workdays": False,
    "time_per_day": (8.0, 8.0, 8.0, 8.0, 8.0, 0, 0),
}
CONFIG_NAMES = Literal[
    "name",
    "save_path",
    "work_hours",
    "use_hours_per_week",
    "country",
    "subdiv",
    "workdays",
    "different_workdays",
    "time_per_day",
]


@dataclass
@dataclass_json
class Config:
    name: str
    save_path: str
    daily_hours: float
    weekly_hours: float
    work_hours: float
    use_hours_per_week: bool
    country: str
    subdiv: str | None
    workdays: list[int]
    different_workdays: bool
    time_per_day: tuple[float, float, float, float, float, float, float]

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "Config":
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

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get_weekly_hours(self) -> float:
        """Get the total work time for the week."""
        if self.different_workdays:
            return sum(self.time_per_day[day] for day in self.workdays)
        if self.use_hours_per_week:
            return self.work_hours
        return self.work_hours * len(self.workdays)

    def get_daily_hours_at(self, day: int) -> float:
        """Get the work time for a specific day, 0-6, 0=Monday, 6=Sunday."""
        if day not in self.workdays:
            return 0.0
        if self.different_workdays:
            return self.time_per_day[day]
        number_work_days = len(self.workdays)
        if number_work_days == 0:
            return 0.0
        if not self.use_hours_per_week:
            return self.work_hours / number_work_days
        return self.work_hours

    def get_all_daily_hours(self) -> list[float]:
        """Get the work time for each day, 0-6, 0=Monday, 6=Sunday."""
        return [self.get_daily_hours_at(day) for day in range(7)]

    def get_holidays(self, year: int) -> list[datetime.date]:
        available_holidays = holidays.country_holidays(
            CONFIG_HANDLER.config.country, subdiv=CONFIG_HANDLER.config.subdiv or None, years=year
        )
        return list(available_holidays.keys())


class ConfigHandler:
    def __init__(self) -> None:
        """Class for managing configuration file and settings ."""
        self.config = self._get_config()

    def _get_config(self) -> Config:
        config_file = self.read_config_file()
        return Config.from_kwargs(**config_file)

    def read_config_file(self) -> dict:
        if not CONFIG_PATH.exists():
            return NEEDED_DATA
        with CONFIG_PATH.open(encoding="utf-8") as f:
            config = json.load(f)
        for d in NEEDED_DATA.items():
            if d[0] not in config:
                config[d[0]] = d[1]
        return config

    def write_config_file(self) -> None:
        with CONFIG_PATH.open("w", encoding="utf-8") as write_file:
            # pylint: disable=no-member
            json.dump(self.config.to_dict(), write_file)  # type: ignore

    def set_config_value(self, key: CONFIG_NAMES, value: Any, write: bool = True) -> None:
        setattr(self.config, key, value)
        if not write:
            return
        self.write_config_file()

    def config_hash(self) -> int:
        """Get a hash of the current config."""
        return hash(json.dumps(self.config.to_dict()))  # type: ignore


CONFIG_HANDLER = ConfigHandler()
