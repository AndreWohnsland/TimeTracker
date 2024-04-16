import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot

import qdarktheme
import darkdetect

APP_NAME = "time_tracker"


def get_style_name() -> str:
    is_light: bool = darkdetect.isLight()  # type: ignore
    return "light" if is_light else "dark"


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


@pyqtSlot()
def sync_theme() -> None:
    stylesheet = qdarktheme.load_stylesheet(get_style_name())
    QApplication.instance().setStyleSheet(stylesheet)  # type: ignore
