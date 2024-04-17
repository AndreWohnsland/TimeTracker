from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon

import qdarktheme
import darkdetect

from src.filepath import CLOCK_ICON, CLOCK_ICON_DARK_MODE


def get_style_name() -> str:
    """Returns if the system uses dark or light mode"""
    is_light: bool = darkdetect.isLight()  # type: ignore
    return "light" if is_light else "dark"


def get_icon_color() -> str:
    """Returns the icon color based on the light mode."""
    return "black" if darkdetect.isLight() else "white"


def get_app_icon() -> QIcon:
    """Returns the icon color based on the light mode."""
    return QIcon(str(CLOCK_ICON)) if darkdetect.isLight() else QIcon(str(CLOCK_ICON_DARK_MODE))


@pyqtSlot()
def sync_theme() -> None:
    stylesheet = qdarktheme.load_stylesheet(get_style_name())
    QApplication.instance().setStyleSheet(stylesheet)  # type: ignore
