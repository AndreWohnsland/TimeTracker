import os
import sys
from pathlib import Path

APP_NAME = "time_tracker"


def _sanitize_name(name: str) -> str:
    """Converts spaces to underscores and converts to lowercase."""
    return name.replace(" ", "_").lower()


def get_app_dir(app_name: str = APP_NAME) -> Path:
    """Get the application directory for the current platform."""
    app_name = _sanitize_name(app_name)
    # Windows
    if sys.platform.startswith("win"):
        app_folder = os.environ.get("APPDATA")
        if app_folder is None:
            app_folder = os.path.expanduser("~")
        return Path(app_folder) / app_name
    # MacOS
    if sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Application Support")) / app_name
    # Linux
    return Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))) / app_name


# Root path
ROOT_PATH = Path(__file__).parents[1].absolute()
HOME_PATH = Path.home()

# UI
UI_PATH = ROOT_PATH / "ui"
CLOCK_ICON = UI_PATH / "clock.png"
CLOCK_ICON_DARK_MODE = UI_PATH / "clock_dark_mode.png"

# DB
SAVE_FOLDER = get_app_dir()
OLD_DATABASE_PATH = ROOT_PATH / "data" / "timedata.db"
DATABASE_PATH = SAVE_FOLDER / "time_data.db"

# config
CONFIG_PATH = ROOT_PATH / "config"
CONFIG_FILE = CONFIG_PATH / "config.json"
