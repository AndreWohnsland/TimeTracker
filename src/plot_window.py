import time
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.ticker as ticker
import pandas as pd

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *


class GraphWindow(QDialog):
    def __init__(self, input_df):
        super(GraphWindow, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(1200, 800)
        self.setWindowTitle("Plot of the Working time")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        self.setModal(True)

        # a figure instance to plot on
        plt.rcParams["date.autoformatter.day"] = "%y/%m/%d"
        self.figure = plt.figure(figsize=(13, 8), dpi=128)
        # adds a button to go back
        self.backbutton = QPushButton("< Back")
        # sets the minimum size and the fontsize
        self.backbutton.setMinimumSize(QSize(0, 50))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.backbutton.setFont(font)
        self.backbutton.clicked.connect(lambda: self.close())
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.backbutton)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        # clears the old values and then adds a subplot to isert all the data
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        df = input_df.copy()
        df["pause"] = df["pause"] / 60
        df["work"] = df["worktime"] / 60 - df["pause"]
        df["overtime"] = df["work"] - 8
        df["overtime"] = df["overtime"].clip(lower=0)
        df["work"] = df["work"].clip(upper=8, lower=0)
        plotdf = df[["work", "overtime", "pause"]]
        plotdf.plot.bar(stacked=True, ax=ax, width=0.8, color=["#2693ff", "#ff4e26", "#25cf5e"])
        ax.legend(fancybox=True, framealpha=0.7)
        plt.axhline(8, color="k", ls="--", lw=1)
        ax.xaxis.get_label().set_visible(False)

        ticklabels = [""] * len(df.index)
        ticklabels[::2] = [item.strftime("%y/%m/%d") for item in df.index[::2]]
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
        plt.gcf().autofmt_xdate()

        # plt.tight_layout()
        self.canvas.draw()
