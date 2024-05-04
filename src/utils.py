import os
from pathlib import Path
import platform
from PyQt5.QtWidgets import QApplication

import qdarktheme
import darkdetect

from src.filepath import SAVE_FOLDER, CONFIG_PATH, DATABASE_PATH, OLD_CONFIG_PATH, OLD_DATABASE_PATH, REPORTS_PATH


def is_light() -> bool:
    """Returns if the system uses dark or light mode"""
    return darkdetect.isLight()  # type: ignore


def get_style_name() -> str:
    """Returns if the system uses dark or light mode"""
    return "light" if is_light() else "dark"


def get_background_color() -> str:
    """Returns the icon color based on the light mode."""
    return "#f8f9fa" if is_light() else "#202124"


def get_font_color() -> str:
    """Returns the font color based on the light mode."""
    return "#4d5157" if is_light() else "#e4e7eb"


def sync_theme() -> None:
    stylesheet = qdarktheme.load_stylesheet(get_style_name())
    QApplication.instance().setStyleSheet(stylesheet)  # type: ignore


def get_additional_run_args() -> list[str]:
    """Returns the additional run arguments for the app."""
    system = platform.system()
    # windows need some extra love for the window header to be dark
    if system == "Windows" and not is_light():
        return ["-platform", "windows:darkmode=1"]
    return []


def prepare_data_location_and_files():
    """ "Create the app folder if not exists.
    Move the old config and database files to the new location."""
    # need to create the folder once
    if not SAVE_FOLDER.exists():
        SAVE_FOLDER.mkdir(parents=True)
    if not REPORTS_PATH.exists():
        REPORTS_PATH.mkdir(parents=True)
    # move config file
    if OLD_CONFIG_PATH.exists():
        print(f"Old Config found at {OLD_DATABASE_PATH}, moving to new location to {DATABASE_PATH}")
        OLD_CONFIG_PATH.rename(CONFIG_PATH)
    # move database file
    if OLD_DATABASE_PATH.exists():
        print(f"Old Database found at {OLD_DATABASE_PATH}, moving to new location to {DATABASE_PATH}")
        OLD_DATABASE_PATH.rename(DATABASE_PATH)


def open_folder_in_explorer(p: Path = SAVE_FOLDER):
    system = platform.system()
    resolved_path = str(p.resolve())
    if system == "Windows":
        os.startfile(resolved_path)
    elif system == "Darwin":  # Mac
        os.system(f"open {resolved_path}")
    elif system == "Linux":
        os.system(f"xdg-open {resolved_path}")
