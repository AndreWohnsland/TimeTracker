from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot

import qdarktheme
import darkdetect

from src.filepath import SAVE_FOLDER, CONFIG_PATH, DATABASE_PATH, OLD_CONFIG_PATH, OLD_DATABASE_PATH


def is_light() -> bool:
    """Returns if the system uses dark or light mode"""
    return darkdetect.isLight()  # type: ignore


def get_style_name() -> str:
    """Returns if the system uses dark or light mode"""
    return "light" if is_light() else "dark"


def get_icon_color() -> str:
    """Returns the icon color based on the light mode."""
    return "black" if is_light() else "white"


@pyqtSlot()
def sync_theme() -> None:
    stylesheet = qdarktheme.load_stylesheet(get_style_name())
    QApplication.instance().setStyleSheet(stylesheet)  # type: ignore


def prepare_data_location_and_files():
    """ "Create the app folder if not exists.
    Move the old config and database files to the new location."""
    # need to create the folder once
    if not SAVE_FOLDER.exists():
        SAVE_FOLDER.mkdir(parents=True)
    # move config file
    if OLD_CONFIG_PATH.exists():
        print(f"Old Config found at {OLD_DATABASE_PATH}, moving to new location to {DATABASE_PATH}")
        OLD_CONFIG_PATH.rename(CONFIG_PATH)
    # move database file
    if OLD_DATABASE_PATH.exists():
        print(f"Old Database found at {OLD_DATABASE_PATH}, moving to new location to {DATABASE_PATH}")
        OLD_DATABASE_PATH.rename(DATABASE_PATH)
