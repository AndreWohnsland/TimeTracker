# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\config_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ConfigWindow(object):
    def setupUi(self, ConfigWindow):
        ConfigWindow.setObjectName("ConfigWindow")
        ConfigWindow.resize(748, 388)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(ConfigWindow)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.scrollArea = QtWidgets.QScrollArea(ConfigWindow)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollArea.setLineWidth(1)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 730, 258))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setContentsMargins(0, 0, 4, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.filter_subdiv = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.filter_subdiv.setMinimumSize(QtCore.QSize(0, 35))
        self.filter_subdiv.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.filter_subdiv.setFont(font)
        self.filter_subdiv.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.filter_subdiv.setObjectName("filter_subdiv")
        self.gridLayout_2.addWidget(self.filter_subdiv, 4, 3, 1, 1)
        self.filter_country = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.filter_country.setMinimumSize(QtCore.QSize(0, 35))
        self.filter_country.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.filter_country.setFont(font)
        self.filter_country.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.filter_country.setObjectName("filter_country")
        self.gridLayout_2.addWidget(self.filter_country, 3, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 4, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 4, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_10.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 5, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_9.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 2, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 3, 2, 1, 1)
        self.input_country = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.input_country.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_country.setFont(font)
        self.input_country.setObjectName("input_country")
        self.gridLayout_2.addWidget(self.input_country, 3, 1, 1, 1)
        self.input_subdiv = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.input_subdiv.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_subdiv.setFont(font)
        self.input_subdiv.setObjectName("input_subdiv")
        self.gridLayout_2.addWidget(self.input_subdiv, 4, 1, 1, 1)
        self.input_name = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.input_name.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_name.setFont(font)
        self.input_name.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.input_name.setObjectName("input_name")
        self.gridLayout_2.addWidget(self.input_name, 0, 1, 1, 3)
        self.input_daily_hours = QtWidgets.QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.input_daily_hours.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_daily_hours.setFont(font)
        self.input_daily_hours.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.input_daily_hours.setObjectName("input_daily_hours")
        self.gridLayout_2.addWidget(self.input_daily_hours, 1, 1, 1, 3)
        self.input_weekly_hours = QtWidgets.QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.input_weekly_hours.setMinimumSize(QtCore.QSize(0, 35))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.input_weekly_hours.setFont(font)
        self.input_weekly_hours.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.input_weekly_hours.setObjectName("input_weekly_hours")
        self.gridLayout_2.addWidget(self.input_weekly_hours, 2, 1, 1, 3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radio_weekday_0 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_0.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_0.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_0.setFont(font)
        self.radio_weekday_0.setAutoExclusive(False)
        self.radio_weekday_0.setObjectName("radio_weekday_0")
        self.horizontalLayout_2.addWidget(self.radio_weekday_0)
        self.radio_weekday_1 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_1.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_1.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_1.setFont(font)
        self.radio_weekday_1.setAutoExclusive(False)
        self.radio_weekday_1.setObjectName("radio_weekday_1")
        self.horizontalLayout_2.addWidget(self.radio_weekday_1)
        self.radio_weekday_2 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_2.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_2.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_2.setFont(font)
        self.radio_weekday_2.setAutoExclusive(False)
        self.radio_weekday_2.setObjectName("radio_weekday_2")
        self.horizontalLayout_2.addWidget(self.radio_weekday_2)
        self.radio_weekday_3 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_3.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_3.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_3.setFont(font)
        self.radio_weekday_3.setAutoExclusive(False)
        self.radio_weekday_3.setObjectName("radio_weekday_3")
        self.horizontalLayout_2.addWidget(self.radio_weekday_3)
        self.radio_weekday_4 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_4.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_4.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_4.setFont(font)
        self.radio_weekday_4.setAutoExclusive(False)
        self.radio_weekday_4.setObjectName("radio_weekday_4")
        self.horizontalLayout_2.addWidget(self.radio_weekday_4)
        self.radio_weekday_5 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_5.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_5.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_5.setFont(font)
        self.radio_weekday_5.setAutoExclusive(False)
        self.radio_weekday_5.setObjectName("radio_weekday_5")
        self.horizontalLayout_2.addWidget(self.radio_weekday_5)
        self.radio_weekday_6 = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
        self.radio_weekday_6.setMinimumSize(QtCore.QSize(0, 35))
        self.radio_weekday_6.setMaximumSize(QtCore.QSize(60, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.radio_weekday_6.setFont(font)
        self.radio_weekday_6.setAutoExclusive(False)
        self.radio_weekday_6.setObjectName("radio_weekday_6")
        self.horizontalLayout_2.addWidget(self.radio_weekday_6)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 5, 1, 1, 3)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.apply_button = QtWidgets.QPushButton(ConfigWindow)
        self.apply_button.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.apply_button.setFont(font)
        self.apply_button.setObjectName("apply_button")
        self.verticalLayout.addWidget(self.apply_button)

        self.retranslateUi(ConfigWindow)
        QtCore.QMetaObject.connectSlotsByName(ConfigWindow)

    def retranslateUi(self, ConfigWindow):
        _translate = QtCore.QCoreApplication.translate
        ConfigWindow.setWindowTitle(_translate("ConfigWindow", "Settings"))
        self.label_5.setText(_translate("ConfigWindow", "<html><head/><body><p>Change your local settings.</p><p>Use decimals for minutes, e.g. 30 minutes are 30/60 = 0.5 h.</p></body></html>"))
        self.label_2.setText(_translate("ConfigWindow", "Name:"))
        self.label_4.setText(_translate("ConfigWindow", "Country:"))
        self.label_8.setText(_translate("ConfigWindow", "Filter:"))
        self.label_3.setText(_translate("ConfigWindow", "Daily Hours:"))
        self.label_6.setText(_translate("ConfigWindow", "Subdiv:"))
        self.label_10.setText(_translate("ConfigWindow", "Workdays:"))
        self.label_9.setText(_translate("ConfigWindow", "Weekly Hours:"))
        self.label_7.setText(_translate("ConfigWindow", "Filter:"))
        self.radio_weekday_0.setText(_translate("ConfigWindow", "Mon"))
        self.radio_weekday_1.setText(_translate("ConfigWindow", "Tue"))
        self.radio_weekday_2.setText(_translate("ConfigWindow", "Wed"))
        self.radio_weekday_3.setText(_translate("ConfigWindow", "Thu"))
        self.radio_weekday_4.setText(_translate("ConfigWindow", "Fri"))
        self.radio_weekday_5.setText(_translate("ConfigWindow", "Sat"))
        self.radio_weekday_6.setText(_translate("ConfigWindow", "Sun"))
        self.apply_button.setText(_translate("ConfigWindow", "Apply"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigWindow = QtWidgets.QWidget()
    ui = Ui_ConfigWindow()
    ui.setupUi(ConfigWindow)
    ConfigWindow.show()
    sys.exit(app.exec_())
