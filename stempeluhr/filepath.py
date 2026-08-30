import os
import sys
from pathlib import Path

APP_NAME = "stempeluhr"
# data dir of installs from before the rename to stempeluhr; never migrated
LEGACY_APP_NAME = "time_tracker"


def _sanitize_name(name: str) -> str:
    """Convert spaces to underscores and converts to lowercase."""
    return name.replace(" ", "_").lower()


def get_app_dir(app_name: str = APP_NAME) -> Path:
    """Get the application directory for the current platform."""
    app_name = _sanitize_name(app_name)
    # Windows
    if sys.platform.startswith("win"):
        app_folder = os.environ.get("APPDATA")
        if app_folder is None:
            app_folder = os.path.expanduser("~")  # noqa: PTH111
        return Path(app_folder) / app_name
    # MacOS
    if sys.platform == "darwin":
        return Path("~/Library/Application Support").expanduser() / app_name
    # Linux
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path("~/.config").expanduser()))) / app_name


# Repo root for git-based installs (points into site-packages for pip installs)
ROOT_PATH = Path(__file__).resolve().parents[1]
PACKAGE_PATH = Path(__file__).resolve().parent
HOME_PATH = Path.home()

# Data folder (app data): keep the pre-rename dir if it already exists
_legacy_folder = get_app_dir(LEGACY_APP_NAME)
SAVE_FOLDER = _legacy_folder if _legacy_folder.exists() else get_app_dir()

# DB
OLD_DATABASE_PATH = ROOT_PATH / "data" / "timedata.db"
DATABASE_PATH = SAVE_FOLDER / "time_data.db"

# config
OLD_CONFIG_PATH = ROOT_PATH / "config" / "config.json"
CONFIG_PATH = SAVE_FOLDER / "config.json"

# saved reports (default one)
REPORTS_PATH = SAVE_FOLDER / "reports"

# Logs
LOG_FILE_PATH = SAVE_FOLDER / "app.log"

# Alembic
MIGRATIONS_PATH = PACKAGE_PATH / "migrations"
