from __future__ import annotations
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.ticker as ticker
import pandas as pd

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout

if TYPE_CHECKING:
    from src.ui_mainwindow import MainWindow


class GraphWindow(QDialog):
    def __init__(self, main_window: MainWindow, input_df: pd.DataFrame):
        super(GraphWindow, self).__init__()
        self.main_window = main_window
        self.setAttribute(Qt.WA_DeleteOnClose)  # type: ignore
        self.resize(1200, 800)
        self.setWindowTitle("Plot of the Working time")
        self.setWindowIcon(self.main_window.clock_icon)
        self.setWindowFlags(
            Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint  # type: ignore
        )
        self.setModal(True)

        # a figure instance to plot on
        plt.rcParams["date.autoformatter.day"] = "%y/%m/%d"
        self.figure = plt.figure(figsize=(13, 8), dpi=128)
        # adds a button to go back
        self.back_button = QPushButton("< Back")
        # sets the minimum size and the fontsize
        self.back_button.setMinimumSize(QSize(0, 50))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.back_button.setFont(font)
        self.back_button.clicked.connect(self.close)  # type: ignore
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.back_button)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        # clears the old values and then adds a subplot to insert all the data
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        df = input_df.copy()
        df["pause"] = df["pause"] / 60
        df["work"] = df["work_time"] / 60 - df["pause"]
        df["overtime"] = df["work"] - 8
        df["overtime"] = df["overtime"].clip(lower=0)
        df["work"] = df["work"].clip(upper=8, lower=0)
        plot_df = df[["work", "overtime", "pause"]]
        plot_df.plot.bar(stacked=True, ax=ax, width=0.8, color=["#2693ff", "#ff4e26", "#25cf5e"])
        ax.legend(fancybox=True, framealpha=0.7)
        plt.axhline(8, color="k", ls="--", lw=1)
        ax.xaxis.get_label().set_visible(False)

        tick_labels = [""] * len(df.index)
        tick_labels[::2] = [item.strftime("%y/%m/%d") for item in df.index[::2]]
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(tick_labels))
        plt.gcf().autofmt_xdate()

        # plt.tight_layout()
        self.canvas.draw()
