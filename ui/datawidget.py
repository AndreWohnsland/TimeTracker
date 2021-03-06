# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\datawidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DataWidget(object):
    def setupUi(self, DataWidget):
        DataWidget.setObjectName("DataWidget")
        DataWidget.resize(596, 570)
        self.verticalLayout = QtWidgets.QVBoxLayout(DataWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.export_button = QtWidgets.QPushButton(DataWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.export_button.setFont(font)
        self.export_button.setObjectName("export_button")
        self.horizontalLayout.addWidget(self.export_button)
        self.plot_button = QtWidgets.QPushButton(DataWidget)
        self.plot_button.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.plot_button.setFont(font)
        self.plot_button.setCheckable(True)
        self.plot_button.setObjectName("plot_button")
        self.horizontalLayout.addWidget(self.plot_button)
        self.switch_button = QtWidgets.QPushButton(DataWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.switch_button.setFont(font)
        self.switch_button.setCheckable(True)
        self.switch_button.setObjectName("switch_button")
        self.horizontalLayout.addWidget(self.switch_button)
        self.date_edit = QtWidgets.QDateEdit(DataWidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.date_edit.setFont(font)
        self.date_edit.setCurrentSection(QtWidgets.QDateTimeEdit.DaySection)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate(2020, 7, 1))
        self.date_edit.setObjectName("date_edit")
        self.horizontalLayout.addWidget(self.date_edit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableWidget = QtWidgets.QTableWidget(DataWidget)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(14)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(14)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(100)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setSortIndicatorShown(False)
        self.verticalLayout.addWidget(self.tableWidget)

        self.retranslateUi(DataWidget)
        QtCore.QMetaObject.connectSlotsByName(DataWidget)

    def retranslateUi(self, DataWidget):
        _translate = QtCore.QCoreApplication.translate
        DataWidget.setWindowTitle(_translate("DataWidget", "View your Data"))
        self.export_button.setText(_translate("DataWidget", "Export"))
        self.plot_button.setText(_translate("DataWidget", "Plot"))
        self.switch_button.setText(_translate("DataWidget", "Month"))
        self.date_edit.setDisplayFormat(_translate("DataWidget", "dd/MM/yyyy"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("DataWidget", "Date"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("DataWidget", "Worktime (h)"))
