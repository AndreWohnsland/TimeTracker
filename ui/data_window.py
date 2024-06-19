# Form implementation generated from reading ui file '.\data_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_DataWindow(object):
    def setupUi(self, DataWindow):
        DataWindow.setObjectName("DataWindow")
        DataWindow.resize(1800, 800)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(DataWindow)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.export_button = QtWidgets.QPushButton(parent=DataWindow)
        self.export_button.setMaximumSize(QtCore.QSize(300, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.export_button.setFont(font)
        self.export_button.setObjectName("export_button")
        self.horizontalLayout_3.addWidget(self.export_button)
        self.switch_button = QtWidgets.QPushButton(parent=DataWindow)
        self.switch_button.setMaximumSize(QtCore.QSize(300, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.switch_button.setFont(font)
        self.switch_button.setCheckable(True)
        self.switch_button.setObjectName("switch_button")
        self.horizontalLayout_3.addWidget(self.switch_button)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tableWidget = QtWidgets.QTableWidget(parent=DataWindow)
        self.tableWidget.setMinimumSize(QtCore.QSize(500, 0))
        self.tableWidget.setMaximumSize(QtCore.QSize(600, 16777215))
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
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
        self.delete_event_button = QtWidgets.QPushButton(parent=DataWindow)
        self.delete_event_button.setMinimumSize(QtCore.QSize(0, 50))
        self.delete_event_button.setMaximumSize(QtCore.QSize(600, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.delete_event_button.setFont(font)
        self.delete_event_button.setObjectName("delete_event_button")
        self.verticalLayout.addWidget(self.delete_event_button)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.container = QtWidgets.QVBoxLayout()
        self.container.setObjectName("container")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_month_prev = QtWidgets.QPushButton(parent=DataWindow)
        self.button_month_prev.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.button_month_prev.setFont(font)
        self.button_month_prev.setCheckable(False)
        self.button_month_prev.setObjectName("button_month_prev")
        self.horizontalLayout.addWidget(self.button_month_prev)
        self.date_edit = QtWidgets.QDateEdit(parent=DataWindow)
        self.date_edit.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.date_edit.setFont(font)
        self.date_edit.setCurrentSection(QtWidgets.QDateTimeEdit.Section.DaySection)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate(2020, 7, 1))
        self.date_edit.setObjectName("date_edit")
        self.horizontalLayout.addWidget(self.date_edit)
        self.button_month_next = QtWidgets.QPushButton(parent=DataWindow)
        self.button_month_next.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.button_month_next.setFont(font)
        self.button_month_next.setCheckable(False)
        self.button_month_next.setObjectName("button_month_next")
        self.horizontalLayout.addWidget(self.button_month_next)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.radio_month = QtWidgets.QRadioButton(parent=DataWindow)
        self.radio_month.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_month.setFont(font)
        self.radio_month.setChecked(True)
        self.radio_month.setObjectName("radio_month")
        self.plot_type_group = QtWidgets.QButtonGroup(DataWindow)
        self.plot_type_group.setObjectName("plot_type_group")
        self.plot_type_group.addButton(self.radio_month)
        self.horizontalLayout.addWidget(self.radio_month)
        self.radio_year = QtWidgets.QRadioButton(parent=DataWindow)
        self.radio_year.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_year.setFont(font)
        self.radio_year.setObjectName("radio_year")
        self.plot_type_group.addButton(self.radio_year)
        self.horizontalLayout.addWidget(self.radio_year)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.save_button = QtWidgets.QPushButton(parent=DataWindow)
        self.save_button.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout.addWidget(self.save_button)
        self.container.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.container)

        self.retranslateUi(DataWindow)
        QtCore.QMetaObject.connectSlotsByName(DataWindow)

    def retranslateUi(self, DataWindow):
        _translate = QtCore.QCoreApplication.translate
        DataWindow.setWindowTitle(_translate("DataWindow", "View your Data"))
        self.export_button.setText(_translate("DataWindow", "Export"))
        self.switch_button.setText(_translate("DataWindow", "Month"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("DataWindow", "Date"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("DataWindow", "Worktime (h)"))
        self.delete_event_button.setText(_translate("DataWindow", "Delete Event"))
        self.button_month_prev.setText(_translate("DataWindow", "<"))
        self.date_edit.setDisplayFormat(_translate("DataWindow", "dd/MM/yyyy"))
        self.button_month_next.setText(_translate("DataWindow", ">"))
        self.radio_month.setText(_translate("DataWindow", "Month"))
        self.radio_year.setText(_translate("DataWindow", "Year"))
        self.save_button.setText(_translate("DataWindow", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DataWindow = QtWidgets.QWidget()
    ui = Ui_DataWindow()
    ui.setupUi(DataWindow)
    DataWindow.show()
    sys.exit(app.exec())
