import sys
from PyQt5.QtWidgets import QApplication

from src.utils import sync_theme
from src.ui_mainwindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    # in case of active style change, also change theme, need to sync at start
    app.paletteChanged.connect(sync_theme)
    # still keep the app running, even if the main window is closed (we use tray for the app)
    QApplication.setQuitOnLastWindowClosed(False)
    sync_theme()
    w.show()
    sys.exit(app.exec_())
