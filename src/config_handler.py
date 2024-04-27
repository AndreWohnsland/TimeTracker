from dataclasses import dataclass
from dataclasses_json import dataclass_json
from inspect import signature
import json
from src.filepath import CONFIG_PATH


# Fill data currently not in the config file,
# need at least all that config has
NEEDED_DATA = {
    "name": "",
    "save_path": "",
    "country": "US",
    "subdiv": None,
}


@dataclass
@dataclass_json
class Config:
    name: str
    save_path: str
    country: str
    subdiv: str | None

    @classmethod
    def from_kwargs(cls, **kwargs):
        cls_fields = {field for field in signature(cls).parameters}

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


class ConfigHandler:
    def __init__(self):
        self.config_path = CONFIG_PATH
        self.config = self.get_config_file_data()

    def get_config_file_data(self):
        config_file = self.read_config_file()
        return Config.from_kwargs(**config_file)

    def read_config_file(self) -> dict:
        if not self.config_path.exists():
            return NEEDED_DATA
        with open(self.config_path, "r") as f:
            config = json.load(f)
        for d in NEEDED_DATA.items():
            if d[0] not in config:
                config[d[0]] = d[1]
        return config

    def write_config_file(self):
        with open(self.config_path, "w") as write_file:
            json.dump(self.config.to_json(), write_file)  # type: ignore

    def set_config_value(self, key, value, write=True):
        setattr(self.config, key, value)
        if not write:
            return
        self.write_config_file()


CONFIG_HANDLER = ConfigHandler()
