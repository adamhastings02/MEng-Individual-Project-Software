# Form implementation generated from reading ui file 'c:\Users\Adam\OneDrive - University of Leeds\University Of Leeds Year 4\5870M - Individual Project\Python Files\dist\guis\mainwindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1350, 875)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        MainWindow.setStyleSheet("background-color: beige;")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.but_manual = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_manual.setGeometry(QtCore.QRect(1220, 360, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_manual.setFont(font)
        self.but_manual.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.but_manual.setStyleSheet("background-color: lightgrey;")
        self.but_manual.setObjectName("but_manual")
        self.lab_dataset = QtWidgets.QLabel(parent=self.centralwidget)
        self.lab_dataset.setGeometry(QtCore.QRect(30, 40, 211, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lab_dataset.setFont(font)
        self.lab_dataset.setObjectName("lab_dataset")
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(250, 40, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.lab_query = QtWidgets.QLabel(parent=self.centralwidget)
        self.lab_query.setGeometry(QtCore.QRect(20, 320, 281, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lab_query.setFont(font)
        self.lab_query.setObjectName("lab_query")
        self.ent_manual = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.ent_manual.setGeometry(QtCore.QRect(30, 360, 1161, 31))
        self.ent_manual.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.ent_manual.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.ent_manual.setObjectName("ent_manual")
        self.table_results = QtWidgets.QTableView(parent=self.centralwidget)
        self.table_results.setGeometry(QtCore.QRect(30, 450, 1281, 201))
        self.table_results.setStyleSheet("background-color: #F5F5DC;")
        self.table_results.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.table_results.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.table_results.setObjectName("table_results")
        self.leedslogo = QtWidgets.QLabel(parent=self.centralwidget)
        self.leedslogo.setGeometry(QtCore.QRect(50, 680, 311, 91))
        self.leedslogo.setText("")
        self.leedslogo.setPixmap(QtGui.QPixmap("c:\\Users\\Adam\\OneDrive - University of Leeds\\University Of Leeds Year 4\\5870M - Individual Project\\Python Files\\dist\\guis\\leeds2.png"))
        self.leedslogo.setScaledContents(True)
        self.leedslogo.setObjectName("leedslogo")
        self.nhslogo = QtWidgets.QLabel(parent=self.centralwidget)
        self.nhslogo.setGeometry(QtCore.QRect(1040, 680, 271, 101))
        self.nhslogo.setText("")
        self.nhslogo.setPixmap(QtGui.QPixmap("c:\\Users\\Adam\\OneDrive - University of Leeds\\University Of Leeds Year 4\\5870M - Individual Project\\Python Files\\dist\\guis\\nhs.jpeg"))
        self.nhslogo.setScaledContents(True)
        self.nhslogo.setObjectName("nhslogo")
        self.but_export = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_export.setGeometry(QtCore.QRect(510, 680, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_export.setFont(font)
        self.but_export.setStyleSheet("background-color: lightgrey;")
        self.but_export.setObjectName("but_export")
        self.lab_results = QtWidgets.QLabel(parent=self.centralwidget)
        self.lab_results.setGeometry(QtCore.QRect(20, 410, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lab_results.setFont(font)
        self.lab_results.setObjectName("lab_results")
        self.lab_title = QtWidgets.QLabel(parent=self.centralwidget)
        self.lab_title.setGeometry(QtCore.QRect(540, 10, 471, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.lab_title.setFont(font)
        self.lab_title.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.lab_title.setObjectName("lab_title")
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(450, 60, 861, 241))
        self.textEdit.setAutoFillBackground(False)
        self.textEdit.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.textEdit.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.textEdit.setObjectName("textEdit")
        self.but_clear = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_clear.setGeometry(QtCore.QRect(510, 720, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_clear.setFont(font)
        self.but_clear.setStyleSheet("background-color: lightgrey;")
        self.but_clear.setObjectName("but_clear")
        self.but_help = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_help.setGeometry(QtCore.QRect(810, 720, 131, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_help.setFont(font)
        self.but_help.setStyleSheet("background-color: lightgrey;")
        self.but_help.setObjectName("but_help")
        self.but_expand = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_expand.setGeometry(QtCore.QRect(1180, 410, 131, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_expand.setFont(font)
        self.but_expand.setStyleSheet("background-color: lightgrey;")
        self.but_expand.setObjectName("but_expand")
        self.but_star = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_star.setGeometry(QtCore.QRect(100, 150, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_star.setFont(font)
        self.but_star.setObjectName("but_star")
        self.but_or = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_or.setGeometry(QtCore.QRect(320, 180, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_or.setFont(font)
        self.but_or.setObjectName("but_or")
        self.but_not = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_not.setGeometry(QtCore.QRect(320, 210, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_not.setFont(font)
        self.but_not.setObjectName("but_not")
        self.but_except = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_except.setGeometry(QtCore.QRect(320, 240, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_except.setFont(font)
        self.but_except.setObjectName("but_except")
        self.but_and = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_and.setGeometry(QtCore.QRect(320, 150, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_and.setFont(font)
        self.but_and.setObjectName("but_and")
        self.but_q = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_q.setGeometry(QtCore.QRect(100, 180, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_q.setFont(font)
        self.but_q.setObjectName("but_q")
        self.but_und = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_und.setGeometry(QtCore.QRect(100, 210, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_und.setFont(font)
        self.but_und.setObjectName("but_und")
        self.lab_query_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lab_query_2.setGeometry(QtCore.QRect(110, 120, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(True)
        self.lab_query_2.setFont(font)
        self.lab_query_2.setObjectName("lab_query_2")
        self.lab_query_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.lab_query_3.setGeometry(QtCore.QRect(320, 120, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(True)
        self.lab_query_3.setFont(font)
        self.lab_query_3.setObjectName("lab_query_3")
        self.but_termfind = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_termfind.setGeometry(QtCore.QRect(810, 680, 131, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_termfind.setFont(font)
        self.but_termfind.setStyleSheet("background-color: lightgrey;")
        self.but_termfind.setObjectName("but_termfind")
        self.but_near = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_near.setGeometry(QtCore.QRect(100, 240, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_near.setFont(font)
        self.but_near.setObjectName("but_near")
        self.but_variables = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_variables.setGeometry(QtCore.QRect(100, 270, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_variables.setFont(font)
        self.but_variables.setObjectName("but_variables")
        self.but_custom = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_custom.setGeometry(QtCore.QRect(320, 270, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_custom.setFont(font)
        self.but_custom.setObjectName("but_custom")
        self.check_anonymise = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.check_anonymise.setGeometry(QtCore.QRect(330, 320, 121, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.check_anonymise.setFont(font)
        self.check_anonymise.setObjectName("check_anonymise")
        self.but_quit = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_quit.setGeometry(QtCore.QRect(660, 720, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_quit.setFont(font)
        self.but_quit.setStyleSheet("background-color: lightgrey;")
        self.but_quit.setObjectName("but_quit")
        self.but_decline = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_decline.setGeometry(QtCore.QRect(1220, 310, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_decline.setFont(font)
        self.but_decline.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.but_decline.setStyleSheet("background-color: #FFB6C1;")
        self.but_decline.setObjectName("but_decline")
        self.but_approve = QtWidgets.QPushButton(parent=self.centralwidget)
        self.but_approve.setGeometry(QtCore.QRect(1110, 310, 93, 28))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.but_approve.setFont(font)
        self.but_approve.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.but_approve.setStyleSheet("background-color: #90EE90;")
        self.but_approve.setObjectName("but_approve")
        self.dateEdit = QtWidgets.QDateEdit(parent=self.centralwidget)
        self.dateEdit.setGeometry(QtCore.QRect(250, 80, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dateEdit.setFont(font)
        self.dateEdit.setStyleSheet("background-color: light;")
        self.dateEdit.setMinimumDateTime(QtCore.QDateTime(QtCore.QDate(1900, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateEdit.setMaximumDate(QtCore.QDate(3000, 12, 31))
        self.dateEdit.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.dateCombo = QtWidgets.QComboBox(parent=self.centralwidget)
        self.dateCombo.setGeometry(QtCore.QRect(30, 80, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.dateCombo.setFont(font)
        self.dateCombo.setObjectName("dateCombo")
        self.dateCombo.addItem("")
        self.dateCombo.addItem("")
        self.dateCombo.addItem("")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1350, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.but_manual.setText(_translate("MainWindow", "Search"))
        self.but_manual.setShortcut(_translate("MainWindow", "Return"))
        self.lab_dataset.setText(_translate("MainWindow", "Please choose the data set:"))
        self.comboBox.setCurrentText(_translate("MainWindow", "Select"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Select"))
        self.comboBox.setItemText(1, _translate("MainWindow", "transcripts.csv"))
        self.comboBox.setItemText(2, _translate("MainWindow", "beers.csv"))
        self.comboBox.setItemText(3, _translate("MainWindow", "medical.csv"))
        self.lab_query.setText(_translate("MainWindow", "Please start to form the search query:"))
        self.leedslogo.setToolTip(_translate("MainWindow", "An image displaying the University of Leeds logo"))
        self.nhslogo.setToolTip(_translate("MainWindow", "An image displaying the NHS logo"))
        self.but_export.setText(_translate("MainWindow", "Export"))
        self.lab_results.setText(_translate("MainWindow", "Results:"))
        self.lab_title.setText(_translate("MainWindow", "Welcome to the Radiology Report Examination Tool!"))
        self.but_clear.setText(_translate("MainWindow", "Clear All"))
        self.but_help.setText(_translate("MainWindow", "Help"))
        self.but_expand.setText(_translate("MainWindow", "Expand Record"))
        self.but_star.setText(_translate("MainWindow", "*"))
        self.but_or.setText(_translate("MainWindow", "OR"))
        self.but_not.setText(_translate("MainWindow", "NOT"))
        self.but_except.setText(_translate("MainWindow", "EXCEPT"))
        self.but_and.setText(_translate("MainWindow", "AND"))
        self.but_q.setText(_translate("MainWindow", "?"))
        self.but_und.setText(_translate("MainWindow", "_"))
        self.lab_query_2.setText(_translate("MainWindow", "Wildcards:"))
        self.lab_query_3.setText(_translate("MainWindow", "Expressions:"))
        self.but_termfind.setText(_translate("MainWindow", "Term Finder"))
        self.but_near.setText(_translate("MainWindow", "NEAR"))
        self.but_variables.setText(_translate("MainWindow", "Variables"))
        self.but_custom.setText(_translate("MainWindow", "Custom"))
        self.check_anonymise.setText(_translate("MainWindow", "Anonymise"))
        self.but_quit.setText(_translate("MainWindow", "Quit"))
        self.but_decline.setText(_translate("MainWindow", "Decline"))
        self.but_approve.setText(_translate("MainWindow", "Approve"))
        self.dateCombo.setCurrentText(_translate("MainWindow", "No Date Filtering"))
        self.dateCombo.setItemText(0, _translate("MainWindow", "No Date Filtering"))
        self.dateCombo.setItemText(1, _translate("MainWindow", "Before"))
        self.dateCombo.setItemText(2, _translate("MainWindow", "After"))