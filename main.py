# Imports
import sys
import spacy
import sqlite3
from bcrypt import checkpw
from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor, QFont
from PyQt6.QtCore import Qt, QTimer
from MainWindow import Ui_MainWindow
from Loading import Ui_Loading
from Login import Ui_Login
from Help import Ui_Help
from Mesh import Ui_Mesh
from Dataselect import Ui_Data
from time import sleep
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from nlprules.preprocessing import clean_dataframe, remove_stopwords, remove_negated_phrases
from nlprules.radexpressions import evaluate_regex, get_regex_proximity, get_regex_wildcards, string_search
from nlprules.dfsearch import check_all_matches, search_dataframe, evaluate_sentences, list_to_string
from nlprules.expression import Expression

# Useful Commands:
# pyuic6 mainwindow.ui -o MainWindow.py
# pipenv shell
# python main.py

def box_clear(self):
    """
    A function which clears all of the text boxes, and resets the combo and spin boxes
    """
    # Clear the manual entry text entry
    self.ent_manual.clear()

    # Clear the results table
    self.table_results.setModel(None)

    # Clear the expanded record text entry
    self.textEdit.clear()

    # Reset the dataset
    self.comboBox.setCurrentText("Select")

def init_errors(self):
    """
    A function to inistialise the error messages used throughout the program
    """
    # Error for no dataset
    self.dataset_error = QMessageBox()
    self.dataset_error.setIcon(QMessageBox.Icon.Critical)
    self.dataset_error.setWindowTitle('Error')
    self.dataset_error.setText('Please Select a Dataset!')

    # Error for no characters in manual search
    self.manual_error = QMessageBox()
    self.manual_error.setIcon(QMessageBox.Icon.Critical)
    self.manual_error.setWindowTitle('Error')
    self.manual_error.setText('Please type something!')

    # Info pop-up for no records found after a search
    self.nothing_error = QMessageBox()
    self.nothing_error.setIcon(QMessageBox.Icon.Information)
    self.nothing_error.setWindowTitle('Information')
    self.nothing_error.setText('No records found')

    # Info pop-up for no records found after a MeSH search
    self.mesh_error = QMessageBox()
    self.mesh_error.setIcon(QMessageBox.Icon.Information)
    self.mesh_error.setWindowTitle('Information')
    self.mesh_error.setText('No synonyms available for this search')

    # Info pop-up for unsuccesful login
    self.login_error = QMessageBox()
    self.login_error.setIcon(QMessageBox.Icon.Critical)
    self.login_error.setWindowTitle('Login Information')
    self.login_error.setText('Login Failed! Please try again')

def init_tooltips(self):
    """
    A function which sets up the tool tips to assist the usability of the program
    """
    # Wildcard Information
    wildtips = str("None : If you don't wish to select a wildcard"+'\n'+
               "* : The * wildcard matches any number of characters"+'\n'+
               "? : The ? wildcard matches any single character"+'\n'+
               "_ : The _ wildcard enforces a word boundary")
    self.ent_wild1.setToolTip(wildtips)
    self.ent_wild2.setToolTip(wildtips)
    self.ent_wild3.setToolTip(wildtips)
    self.ent_wild4.setToolTip(wildtips)

    # Expression Information
    exprtips = str("None : If you don't wish to select an expression"+'\n'+
               "~ : Use proximity operator ~X to search for words that are X near each other"+'\n'+
               "AND: The logical AND operator returns values if both terms are true and returns false otherwise"+'\n'+
               "OR: The logical OR operator returns values if either terms are true and returns false if neither are" +'\n'+
               "NOT: The logical NOT operator returns values if that term isn't there"+'\n'+
               "EXCEPT: The logical EXCEPT operator means AND NOT"+'\n'+
               "NEAR: Use proximity operator NEARX to search for words that are X near each other")
    self.ent_expr1.setToolTip(exprtips)
    self.ent_expr2.setToolTip(exprtips)
    self.ent_expr3.setToolTip(exprtips)

def init_shortcuts(self):
    """
    A function which houses any shortcuts for the main window
    """
    self.but_and.setShortcut("Ctrl+A")

def data_retrieval(dataset):
    """
    Retrieves the selected dataset, cleans the data and removes all stopwords

    Args:
        dataset (str): The dataset name from the combo box

    Returns:
        df_data2: The polished dataframe
    """
    # Data imports
    file_path = dataset
    df_data0 = pd.read_csv(file_path)
    #df_data3 = df_data0.sample(n=100)
    df_data0.fillna('', inplace=True)
    

    # RAW DATA TABLE
    column_report = 'transcription'
    column_description = 'description'
    column_samplename = 'sample_name'
    column_speciality = 'medical_speciality'

    #CLEANED DATA
    df_data = clean_dataframe(df_data0, [column_report], 
                            drop_duplicates=True, # drop duplicate entries
                            drop_nulls=True, # drop empty reports
                            drop_negatives=True, # remove negated phrases
                            drop_ambiguous=True # remove phrases with ambiguous negation
                            )

    #STOP-WORD REMOVAL
    stop_words = pd.read_csv('data/stopwords.csv').T.values[0]
    df_data2 = remove_stopwords(df_data, [column_report]) # This removes stopwords
    
    return df_data2

def manual_retrieval(self):
    """
    A function which obtains the expression that has been manually entered by the user
        
    Returns:
    result (nested list) - The string of the entered expression parsed into a nested list of boolean operators and search terms
    """
    expression = self.ent_manual.toPlainText()
    expr = Expression()
    result = expr.parse_string(expression)
    return result

def df_search(data, expr):
    df_candidate = data.copy() 
    searched = search_dataframe(df_candidate, column='transcription', expression=expr, 
    new_column_name='term_found', debug_column=True)
    return searched

class TableModel(QtCore.QAbstractTableModel):
    """
    A class which enables a table to be instantiated
    """
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

class LoadWindow(QtWidgets.QMainWindow, Ui_Loading):
    def __init__(self, *args, obj=None, **kwargs):
        super(LoadWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)
        
    def update_progress(self):
        self.progress += 20
        self.progressBar.setValue(self.progress)

        if self.progress >= 100:
            self.timer.stop()
            self.lab_loading.setText("Loading completed.")
            self.close()

class LoginWindow(QtWidgets.QMainWindow, Ui_Login):
    def __init__(self, *args, obj=None, **kwargs):
        super(LoginWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.but_login.clicked.connect(self.login_button_clicked)
        self.but_forgot.clicked.connect(self.forgot_button_clicked)
        init_errors(self)
    
    def login_button_clicked(self):
        username = self.lineEdit_user.text()
        password = self.lineEdit_pass.text()
        conn = sqlite3.connect("UserManagement.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=:username", {"username":username})
        user = c.fetchone()
        global login_success
        login_success = 0
        if user != None and user[1] == username and checkpw(password.encode('utf-8'), user[2]):
            login_success = 1
            self.close()
        else:
            login_success = 0
            self.login_error.exec()
            self.lineEdit_user.clear()
            self.lineEdit_pass.clear()
            self.lineEdit_user.setFocus()
   
    def forgot_button_clicked(self):
        self.help = HelpWindow()
        self.help.show()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.showMaximized()
        self.setStyleSheet("background-color: #F5F5DC;")
        self.table_results.setStyleSheet("background-color: #F5F5DC;")
        self.but_manual.clicked.connect(self.manual_button_clicked)
        self.but_clear.clicked.connect(self.clear_button_clicked)
        self.but_expand.clicked.connect(self.expand_button_clicked)
        self.but_help.clicked.connect(self.help_button_clicked)
        self.but_termfind.clicked.connect(self.term_button_clicked)
        self.but_and.clicked.connect(self.and_button_clicked)
        #init_tooltips(self)
        init_errors(self)
        init_shortcuts(self)

    def manual_button_clicked(self):
        """
        A function which executes when the search button near the manual entry line is clicked
        """
        # Retrieve the selected dataset, and throw an error if not selected. Otherwise retrieve dataset
        selected_dataset = self.comboBox.currentText()
        if selected_dataset == "Select":
            self.dataset_error.exec()
            return
        else:
            data = data_retrieval(selected_dataset)
        # Retrieve the line, and if this is empty, then throw an error. Otherwise create expression object
        man = self.ent_manual.toPlainText()
        if man.strip() == "":
            self.manual_error.exec()
            return
        else:    
            expr = manual_retrieval(self)
        
        # Search the results and filter the dataframe by values which are true under the expression
        results = df_search(data, expr)
        condition = results['term_found'] == True
        filtered_df = results[condition]

        # Perform some data manipulation on the filtered dataframe to create a format valid for the TableModel 
        individual_terms = []
        if len(filtered_df != 0):
            items = list(filtered_df.to_records(index=False))
            for i in items:
                for j in i:
                    individual_terms.append(j)
            
            result_matrix = [individual_terms[i:i+8][1:4] for i in range(0, len(individual_terms), 8)]

            # Create the dataframe and send the contents to the table, with the allocated column headings
            data = pd.DataFrame(result_matrix, columns = ['Description', 'Medical Speciality', 'Sample Name'])
            self.model = TableModel(data)
            self.table_results.setModel(self.model)
            self.table_results.resizeColumnsToContents()
        else:
            self.nothing_error.exec() # Executes if no results for searched expression
     
    def clear_button_clicked(self):
        box_clear(self)

    def expand_button_clicked(self):
        selected_items = self.table_results.selectedIndexes()
        # Iterate over the selected indexes
        for index in selected_items:
            # Get the row and column index of each selected cell
            row = index.row()
            column = index.column()
            # Get the data of the selected cell
            data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)
            # Find the transcription matching the description
            df = pd.read_csv('transcripts.csv')
            result = df[df['sample_name'] == data]
            value = result['transcription']
            text = value.iloc[0]
            self.textEdit.setText(text)
            # Highlight the keywords
            keywords = result['keywords']
            keys = keywords.iloc[0]
            word_list = str(keys).split(',')
            text = self.textEdit.toPlainText()
            highlighted_text = text.lower()
            # Loop through the words and highlight them in bold
            if word_list[0] != 'nan':
                for word in word_list:
                    highlighted_text = highlighted_text.replace(word, f"<b>{word}</b>")

            # Set the highlighted text back to the QTextEdit
            self.textEdit.setHtml(highlighted_text)
   
    def help_button_clicked(self):
        self.help = HelpWindow()
        self.help.show()

    def term_button_clicked(self):
        self.help = MeshWindow()
        self.help.show()
    
    def and_button_clicked(self):
        self.ent_manual.setFocus()
        new_text = " AND "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

class HelpWindow(QtWidgets.QMainWindow, Ui_Help):
    """
    This window appears after the 'Help' button is clicked.
    Contains instructions for the user if they need assistance
    """
    def __init__(self, *args, obj=None, **kwargs):
        super(HelpWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.but_close.clicked.connect(self.close_button_clicked)
        self.showMaximized()
    
    def close_button_clicked(self):
        self.close()

class MeshWindow(QtWidgets.QMainWindow, Ui_Mesh):
    """
    This window appears after the 'Term Finder' button is clicked.
    A MeSH searching window appears, where the user can search for related terms
    """
    def __init__(self, *args, obj=None, **kwargs):
        super(MeshWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.but_search.clicked.connect(self.search_clicked)
        self.but_close.clicked.connect(self.close_clicked)
        init_errors(self)
    
    def search_clicked(self):
        text = self.lineEdit_user.text()
        df = pd.read_csv('synonyms.csv')
        df.fillna('', inplace=True)
        result = df[df['Term'] == text.capitalize()]
        value = result.iloc[:,3:]
        list_of_lists = value.values.tolist()
        flattened_list = [item for sublist in list_of_lists for item in sublist]
        result_string = ', '.join(map(str, flattened_list))
        terms = result_string.split(',')
        cleaned_terms = [term.strip() for term in terms if term.strip()]
        result_string = ', '.join(cleaned_terms)
        if len(result_string) == 0:
            self.textBrowser.clear()
            self.mesh_error.exec()
        else:
            self.textBrowser.setText(result_string)
    
    def close_clicked(self):
        self.close()

class DataWindow(QtWidgets.QMainWindow, Ui_Data):
    def __init__(self, *args, obj=None, **kwargs):
        super(DataWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.comboBox.currentIndexChanged.connect(self.update_table)
        init_errors(self)
    
    def update_table(self):
        self.tableView.setModel(None)
        selected_dataset = self.comboBox.currentText()
        if (selected_dataset != "Select"):
            dataset = data_retrieval(selected_dataset)
            data = pd.DataFrame(dataset.head(), columns = ['No', 'description','medical_specialty','sample_name'])
            self.model = TableModel(data)
            self.tableView.setModel(self.model)
            self.tableView.resizeColumnsToContents()
        else:
            self.tableView.setModel(None)

# Execute the app
app = QtWidgets.QApplication(sys.argv)
window = LoadWindow()
window.show()
app.exec()
sleep(1)
window = LoginWindow()
window.show()
app.exec()
sleep(1)
#try:
if login_success == 1:
    window = MainWindow()
    window.show()
    app.exec()
#except:
    #app.quit()


