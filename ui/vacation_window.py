# Form implementation generated from reading ui file '.\vacation_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_VacationWindow(object):
    def setupUi(self, VacationWindow):
        VacationWindow.setObjectName("VacationWindow")
        VacationWindow.resize(475, 656)
        self.verticalLayout = QtWidgets.QVBoxLayout(VacationWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(parent=VacationWindow)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.date_edit = QtWidgets.QDateEdit(parent=VacationWindow)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.date_edit.setFont(font)
        self.date_edit.setDateTime(QtCore.QDateTime(QtCore.QDate(2024, 1, 1), QtCore.QTime(0, 0, 0)))
        self.date_edit.setCurrentSection(QtWidgets.QDateTimeEdit.Section.DaySection)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QtCore.QDate(2024, 1, 1))
        self.date_edit.setObjectName("date_edit")
        self.horizontalLayout.addWidget(self.date_edit)
        self.save_button = QtWidgets.QPushButton(parent=VacationWindow)
        self.save_button.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.save_button.setFont(font)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout.addWidget(self.save_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.year_select = QtWidgets.QSpinBox(parent=VacationWindow)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.year_select.setFont(font)
        self.year_select.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.year_select.setMinimum(2000)
        self.year_select.setMaximum(2050)
        self.year_select.setProperty("value", 2024)
        self.year_select.setObjectName("year_select")
        self.verticalLayout.addWidget(self.year_select)
        self.label_list_view = QtWidgets.QLabel(parent=VacationWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_list_view.setFont(font)
        self.label_list_view.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_list_view.setObjectName("label_list_view")
        self.verticalLayout.addWidget(self.label_list_view)
        self.scrollArea = QtWidgets.QScrollArea(parent=VacationWindow)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.scrollArea.setLineWidth(1)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 457, 463))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.list_widget_dates = QtWidgets.QListWidget(parent=self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.list_widget_dates.setFont(font)
        self.list_widget_dates.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_widget_dates.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.list_widget_dates.setObjectName("list_widget_dates")
        self.verticalLayout_3.addWidget(self.list_widget_dates)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(VacationWindow)
        QtCore.QMetaObject.connectSlotsByName(VacationWindow)

    def retranslateUi(self, VacationWindow):
        _translate = QtCore.QCoreApplication.translate
        VacationWindow.setWindowTitle(_translate("VacationWindow", "Manage your vacation days"))
        self.label_5.setText(_translate("VacationWindow", "<html><head/><body><p>Enter your vacation days. Each day will count as your configured daily working hour on that day, so no need to enter holidays or weekends here.</p></body></html>"))
        self.date_edit.setDisplayFormat(_translate("VacationWindow", "dd/MM/yyyy"))
        self.save_button.setText(_translate("VacationWindow", "Add"))
        self.label_list_view.setText(_translate("VacationWindow", "List of vacation days in year x"))
        self.list_widget_dates.setSortingEnabled(False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    VacationWindow = QtWidgets.QWidget()
    ui = Ui_VacationWindow()
    ui.setupUi(VacationWindow)
    VacationWindow.show()
    sys.exit(app.exec())
