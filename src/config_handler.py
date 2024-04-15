import json
from src.filepath import CONFIG_FILE


class ConfigHandler:
    def __init__(self):
        self.config_file_path = CONFIG_FILE

    def get_config_file_data(self) -> dict:
        self.check_config()
        config = self.read_config_file()
        return config

    def read_config_file(self) -> dict:
        with open(self.config_file_path, "r") as f:
            config = json.load(f)
        return config

    def write_config_file(self, data: dict):
        with open(self.config_file_path, "w") as write_file:
            json.dump(data, write_file)

    def check_config(self):
        if not self.config_file_path.exists():
            print("File not existing, creating config file")
            data = {"Name": "dummy", "Personal Number": "dummy", "save_path": ""}
            self.write_config_file(data)
