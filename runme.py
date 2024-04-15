import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot

import qdarktheme
import darkdetect

from src.ui_mainwindow import MainWindow

IS_LIGHT: bool = darkdetect.isLight()  # type: ignore
STYLE_NAME = "light" if IS_LIGHT else "dark"


@pyqtSlot()
def sync_theme() -> None:
    stylesheet = qdarktheme.load_stylesheet(STYLE_NAME)
    QApplication.instance().setStyleSheet(stylesheet)  # type: ignore


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    # in case of active style change, also change theme, need to sync at start
    app.paletteChanged.connect(sync_theme)
    sync_theme()
    w.show()
    sys.exit(app.exec_())
