import json
import os
from pathlib import Path


class ConfigHandler:
    def __init__(self):
        dirpath = os.path.dirname(__file__)
        self.config_file_path = os.path.join(dirpath, "..", "config", "config.json")

    def get_config_file_data(self):
        self.check_config()
        config = self.read_config_file()
        return config

    def read_config_file(self):
        with open(self.config_file_path, "r") as f:
            config = json.load(f)
        return config

    def write_config_file(self, data):
        with open(self.config_file_path, "w") as write_file:
            json.dump(data, write_file)

    def check_config(self):
        if not Path(self.config_file_path).exists():
            print("File not existing, creating config file")
            data = {"Name": "dummy", "Personal Number": "dummy", "save_path": ""}
            self.write_config_file(data)
