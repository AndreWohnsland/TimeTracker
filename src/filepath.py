from pathlib import Path
from src.utils import get_app_dir

# Root path
ROOT_PATH = Path(__file__).parents[1].absolute()
HOME_PATH = Path.home()

# UI
UI_PATH = ROOT_PATH / "ui"
CLOCK_ICON = UI_PATH / "clock.png"

# DB
SAVE_FOLDER = get_app_dir()
OLD_DATABASE_PATH = ROOT_PATH / "data" / "timedata.db"
DATABASE_PATH = SAVE_FOLDER / "time_data.db"

# config
CONFIG_PATH = ROOT_PATH / "config"
CONFIG_FILE = CONFIG_PATH / "config.json"
