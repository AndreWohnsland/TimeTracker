from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot

import qdarktheme
import darkdetect


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
