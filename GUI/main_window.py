from PyQt4 import QtCore, QtGui
import sys, time, random

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setObjectName(_fromUtf8("MainWindow"))
        self.resize(208, 133)
        self.centralwidget = QtGui.QWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.ttl_label = QtGui.QLabel(self.centralwidget)
        self.ttl_label.setObjectName(_fromUtf8("ttl_label"))
        self.horizontalLayout.addWidget(self.ttl_label)
        self.ttl_value = QtGui.QSpinBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ttl_value.sizePolicy().hasHeightForWidth())
        self.ttl_value.setSizePolicy(sizePolicy)
        self.ttl_value.setMinimum(1)
        self.ttl_value.setObjectName(_fromUtf8("ttl_value"))
        self.horizontalLayout.addWidget(self.ttl_value)
        self.ttl_button = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ttl_button.sizePolicy().hasHeightForWidth())
        self.ttl_button.setSizePolicy(sizePolicy)
        self.ttl_button.setMinimumSize(QtCore.QSize(85, 0))
        self.ttl_button.setObjectName(_fromUtf8("ttl_button"))
        self.horizontalLayout.addWidget(self.ttl_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.main_panel = QtGui.QTextBrowser(self.centralwidget)
        self.main_panel.setObjectName(_fromUtf8("main_panel"))
        self.gridLayout_2.addWidget(self.main_panel, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.ttl_label.setText(_translate("MainWindow", "TTL:", None))
        self.ttl_button.setText(_translate("MainWindow", "Set", None))

    def print_on_main_panel(self, message):
        self.main_panel.append(message)