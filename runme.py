import sys
from PyQt5.QtWidgets import QApplication

from src.ui_mainwindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
