# General Imports:
import sys
import re
import spacy
from spacy import displacy
from time import sleep
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
# Databse Imports:
import sqlite3
from bcrypt import checkpw
from database import *
# PyQt6 Imports:
from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate
from guis.mainwindow_ui import Ui_MainWindow
from guis.loading_ui import Ui_Loading
from guis.login_ui import Ui_Login
from guis.help_ui import Ui_Help
from guis.Mesh import Ui_Mesh
from guis.variables_ui import Ui_Variables
from guis.custom_ui import Ui_Custom
# RADEX Tool Imports
from nlprules.preprocessing import clean_dataframe, remove_stopwords, remove_negated_phrases
from nlprules.radexpressions import evaluate_regex, get_regex_proximity, get_regex_wildcards, string_search
from nlprules.dfsearch import check_all_matches, search_dataframe, evaluate_sentences, list_to_string
from nlprules.expression import Expression
# Globals declaration list:
global colourdict
colourdict = {"PATHOGEN": "#F67DE3", "MEDICINE": "#7DF6D9", "MEDICALCONDITION":"#a6e22d", "QUANTITY":"#ffffff"}

# Useful Commands:
# pyuic6 mainwindow.ui -o MainWindow.py
# pipenv shell
# python main.py
# pyinstaller --onefile main.py
# To export as an executable, type the above command, and copy across the data, guis, negex
# and nlprules folders to dist folder. May need more folders but still TBD

# Program Begin

def box_clear(self):
    """
    A function which clears all of the text boxes, and resets the combo and spin boxes
    """
    self.ent_manual.clear()                             # Clear the manual entry text entry
    self.table_results.setModel(None)                   # Clear the results table
    self.textEdit.clear()                               # Clear the expanded record text entry
    self.comboBox.setCurrentText("Select")              # Reset the dataset
    self.dateCombo.setCurrentText("No Date Filtering")  # Reset the date option
    self.dateEdit.setDate(QDate.currentDate())          # Reset the date

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

    # Error for duplicates
    self.duplicate_error = QMessageBox()
    self.duplicate_error.setIcon(QMessageBox.Icon.Critical)
    self.duplicate_error.setWindowTitle('Error')
    self.duplicate_error.setText('Duplicates Detected! Please merge any reports with matching CRIS Numbers')

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

    # Info pop-up for incorrect column index selected
    self.index_error = QMessageBox()
    self.index_error.setIcon(QMessageBox.Icon.Critical)
    self.index_error.setWindowTitle('Error')
    self.index_error.setText('Incorrect column index selected! Please select the CRIS_No of the desired record')

    # Are you sure you wish to proceed? (General)
    self.proceed = QMessageBox()
    self.proceed.setIcon(QMessageBox.Icon.Critical)
    self.proceed.setWindowTitle('Confirmation')
    self.proceed.setText('Are you sure you wish to proceed?')
    self.proceed.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    self.proceed.setDefaultButton(QMessageBox.StandardButton.No) 

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
    df_data0 = pd.read_csv('data/'+file_path)
    #df_data3 = df_data0.sample(n=100)
    df_data0.fillna('', inplace=True)

    # RAW DATA TABLE
    column_report = 'Report'
    
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

def df_search(data, expr):
    """
    Performs a REGEX search on a given dataset using a given expression. 
    Main functionality for the program, combining the GUI with the RADEX tool programs

    Args:
        data: The dataset you desire to perform the search upon
        expr: The custom expression written using the manual search line to search the dataframe with

    Returns:
        searched: The original dataframe with a new column that houses the terms found, and their indexes in the report
    """
    df_candidate = data.copy()                          # Make a copy of the dataframe, and then search it by the argument expression
    searched = search_dataframe(df_candidate, column='Report', expression=expr, 
    new_column_name='term_found', debug_column=True)    # Create a new column for the terms_found
    return searched                                     # Return the new dataframe

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
    """
    The first window which appears when executing the app, which is a 
    basic loading screen, with a title, progress bar, logos and supporting text
    Approx loading time (0.75*5) = 3.75s (can be changed on timer start line) 
    """
    def __init__(self, *args, obj=None, **kwargs):
        """
        Function to inistialise loading window
        """
        super(LoadWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)                              # Setup UI
        self.progress = 0                               # Starting progress = 0
        self.timer = QTimer()                           # Create timer object
        self.timer.timeout.connect(self.update_progress)# Connect timer timeout to progress update function 
        self.timer.start(750)                           # 750ms timer for each progress increment
        
    def update_progress(self):
        """
        Function to update the progress of the progress bar 
        """
        self.progress += 20                             # Increment progress by 20
        self.progressBar.setValue(self.progress)        # Assign new value to progress bar

        if self.progress >= 100:                        # If progress bar is full (i.e., 100%)
            self.timer.stop()                           # Stop the timer
            self.lab_loading.setText("Loading completed.")
            self.close()                                # Close the window once complete

class LoginWindow(QtWidgets.QMainWindow, Ui_Login):
    """
    The second window which launches after the loading screen has finished
    A basic login system, which is linked to a SQLite database
    Options to login, quit, and a forgot my password feature
    """
    def __init__(self, *args, obj=None, **kwargs):
        """
        Function to inistialise the login window
        """
        super(LoginWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)                                          # Setup UI
        self.but_login.clicked.connect(self.login_button_clicked)   # Connect login button to function
        self.but_forgot.clicked.connect(self.forgot_button_clicked) # Connect forgot password button to function
        self.but_quit.clicked.connect(self.quit_button_clicked)     # Connect quit button to function
        init_errors(self)                                           # Initialise the error messages
    
    def login_button_clicked(self):
        """
        Function which gets called when the login button is pressed
        """
        username = self.lineEdit_user.text()          # Extract username from lineEdit   
        password = self.lineEdit_pass.text()          # Extract password from lineEdit
        conn = sqlite3.connect("UserManagement.db")   # Connect to the user management database
        c = conn.cursor()                             # Setup a cursor, 'c'
        c.execute("SELECT * FROM users WHERE username=:username", {"username":username})
        user = c.fetchone()                           # Select 1 value from database with matching username
        global login_success                          # Global setup to control if main window is displayed
        login_success = 0                           
        if user != None and user[1] == username and checkpw(password.encode('utf-8'), user[2]):
            login_success = 1                         # If a user is found, and has a matching username, and whose password
            self.close()                              # corresponds to that username, login_sucess = HIGH and window is closed
        else:
            login_success = 0                         # Otherwise, login has failed
            self.login_error.exec()                   # Display login failure dialogue box
            self.lineEdit_user.clear()                # Clear username line
            self.lineEdit_pass.clear()                # Clear password line
            self.lineEdit_user.setFocus()             # Set mouse cursor to usename line
   
    def forgot_button_clicked(self):
        """
        Function which gets called when the forgot password button is pressed
        """
        self.help = HelpWindow()   # Create and display the help window
        self.help.show()

    def quit_button_clicked(self):
        """
        Function which gets called when the quit button is pressed
        """
        app.quit()  # Terminate the app

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
        self.but_variables.clicked.connect(self.variables_button_clicked)
        self.but_or.clicked.connect(self.or_button_clicked)
        self.but_not.clicked.connect(self.not_button_clicked)
        self.but_except.clicked.connect(self.except_button_clicked)
        self.but_custom.clicked.connect(self.custom_button_clicked)
        self.but_star.clicked.connect(self.star_button_clicked)
        self.but_q.clicked.connect(self.q_button_clicked)
        self.but_und.clicked.connect(self.und_button_clicked)
        self.but_quit.clicked.connect(self.quit_button_clicked)
        self.but_near.clicked.connect(self.near_button_clicked)
        self.but_export.clicked.connect(self.export_button_clicked)
        self.but_colours.clicked.connect(self.colours_button_clicked)
        self.check_anonymise.stateChanged.connect(self.anonymise_changed)
        self.dateEdit.setDate(QDate.currentDate())
        

        init_errors(self)

    def manual_button_clicked(self):
        """
        A function which executes when the search button near the manual entry line is clicked
        """
        # Retrieve the selected dataset, and throw an error if not selected. Otherwise retrieve dataset
        selected_dataset = self.comboBox.currentText()
        if selected_dataset == "Select":
            self.dataset_error.exec()               # Error popup for no dataset selected
            return                                  # End function
        else:
            data = data_retrieval(selected_dataset) # Retrieve the dataset

        # Check for duplicate data
        duplicates_exist = data['CRIS_No'].duplicated().any()   # Checks dataframe for any duplicates
        if duplicates_exist:
            self.duplicate_error.exec()                         # If so, popup an error but proceed anyway
        else:
            pass                                                # Otherwise proceed


        # Check to see if they have selected a date to filter by
        filtering_date = self.dateCombo.currentText()                                   # Access if they want to filter the date
        target_date = self.dateEdit.date().toString()                                   # Access current date value and convert to string
        
        if (filtering_date == "Before"):                                                # IF Before is selected
            data['Events_date'] = pd.to_datetime(data['Events_date'], format='%d/%m/%Y')# Format EventsDate column to appropriate format
            data = data[data['Events_date'] <= target_date]                             # Filter dataframe for less than
            data['Events_date'] = data['Events_date'].dt.strftime("%d/%m/%Y")           # Reset the date formatting
        
        elif (filtering_date == "After"):                                               # IF After is selected
            data['Events_date'] = pd.to_datetime(data['Events_date'], format='%d/%m/%Y')# Format EventsDate column to appropriate format
            data = data[data['Events_date'] >= target_date]                             # Filter dataframe for greater than
            data['Events_date'] = data['Events_date'].dt.strftime("%d/%m/%Y")           # Reset the date formatting
        else:
            pass
    
        # Anonymise data if anonymise check box is checked [forenames,surname,dob,age,NHS_no]
        if self.check_anonymise.isChecked():
            data['forenames'] = "John"
            data['surname'] = "Doe"
            data['DOB'] = "DD/MM/YYYY"
            data['Age_at_Exam'] = "NN"
            data['NHS_No'] = "AAA BBB CCC"
        else:
            pass
            
        # Retrieve the line, and if this is empty, then throw an error. Otherwise create expression object
        man = self.ent_manual.toPlainText()         # Read the text in the search bar
        conn = sqlite3.connect("UserManagement.db") # Connect to the user management database
        c = conn.cursor()                           # Setup a cursor, 'c'
        c.execute("SELECT * FROM variables")        # Select all from variables
        variables = c.fetchall()                    # Select all values from database
        
        for var, text in variables:                 # If there is a variable in the text...
            man = man.replace(var, text)            # replace it with the associated text from the database

        if man.strip() == "":                       # If the manual line is empty...
            self.manual_error.exec()                # Popup an error and terminate the funciton
            return
        else:                                       # Otherwise...
            expr = Expression()                     # Create an expression object 
            result = expr.parse_string(man)         # Parse the manual entry line to produce the regex expression
        
        # Search the results and filter the dataframe by values which are true under the expression
        results = df_search(data, result)
        condition = results['term_found'] == True
        filtered_df = results[condition]

        # Sorting Algorithms
        sorting = self.sortCombo.currentText()
        if sorting == "Default":
            pass
        # Age
        elif sorting == "Age - Ascending":
            filtered_df = filtered_df.sort_values(by='Age_at_Exam', ascending=True)
        elif sorting == "Age - Descending":
            filtered_df = filtered_df.sort_values(by='Age_at_Exam', ascending=False)
        # CRIS_No
        elif sorting == "CRISNo - Ascending":
            filtered_df = filtered_df.sort_values(by='CRIS_No', ascending=True)
        elif sorting == "CRISNo - Descending":
            filtered_df = filtered_df.sort_values(by='CRIS_No', ascending=False)
        # Date
        elif sorting == "Date - Ascending":
            filtered_df['Events_date'] = pd.to_datetime(filtered_df['Events_date'], format='%d/%m/%Y')# Format EventsDate column to appropriate format
            filtered_df = filtered_df.sort_values(by='Events_date', ascending=True)                   # Filter dataframe for less than
            filtered_df['Events_date'] = filtered_df['Events_date'].dt.strftime("%d/%m/%Y")         
        elif sorting == "Date - Descending":
            filtered_df['Events_date'] = pd.to_datetime(filtered_df['Events_date'], format='%d/%m/%Y')# Format EventsDate column to appropriate format
            filtered_df = filtered_df.sort_values(by='Events_date', ascending=False)                  # Filter dataframe for less than
            filtered_df['Events_date'] = filtered_df['Events_date'].dt.strftime("%d/%m/%Y") 
        # Event Key
        elif sorting == "EventKey - Ascending":
            filtered_df = filtered_df.sort_values(by='Event_Key', ascending=True)
        elif sorting == "EventKey - Descending":
            filtered_df = filtered_df.sort_values(by='Event_Key', ascending=False)
        # Forename
        elif sorting == "Forename - Ascending":
            filtered_df = filtered_df.sort_values(by='forenames', ascending=True)
        elif sorting == "Forename - Descending":
            filtered_df = filtered_df.sort_values(by='forenames', ascending=False)
        # NHS No
        elif sorting == "NHSNo - Ascending":
            filtered_df = filtered_df.sort_values(by='NHS_No', ascending=True)
        elif sorting == "NHSNo - Descending":
            filtered_df = filtered_df.sort_values(by='NHS_No', ascending=False)
        # NHS No
        elif sorting == "Surname - Ascending":
            filtered_df = filtered_df.sort_values(by='surname', ascending=True)
        elif sorting == "Surname - Descending":
            filtered_df = filtered_df.sort_values(by='surname', ascending=False)

        if len(filtered_df != 0):
            self.model = TableModel(filtered_df)
            self.table_results.setModel(self.model)
            self.table_results.resizeColumnsToContents()
        else:
            self.nothing_error.exec() # Executes if no results for searched expression
     
    def clear_button_clicked(self):
        box_clear(self)

    def expand_button_clicked(self):
        selected_items = self.table_results.selectedIndexes()
        selected_dataset = self.comboBox.currentText()
        nlp_ner = spacy.load("model-best")
        # Iterate over the selected indexes
        for index in selected_items:
            # Get the row and column index of each selected cell
            row = index.row()                                   # Retrieve the row of selected record
            column = index.column()                             # Retrieve column of the selected record
            if column != 0:                                     # If it isnt column zero, present an error
                self.index_error.exec()
                return
            else:    
                # Get the data of the selected cell and proceed
                data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)
        
        # Find the transcription matching the description
        df = data_retrieval(selected_dataset)
        man = self.ent_manual.toPlainText()
        conn = sqlite3.connect("UserManagement.db")                 # Connect to the user management database
        c = conn.cursor()                                           # Setup a cursor, 'c'
        c.execute("SELECT * FROM variables")
        variables = c.fetchall()                                    # Select all values from database
        for var, text in variables:
            man = man.replace(var, text)

        if man.strip() == "":
            self.manual_error.exec()
            return
        else:    
            expr = Expression()
            result = expr.parse_string(man)
        
        # Search the results and filter the dataframe by values which are true under the expression
        results = df_search(df, result)
        result = results[results['CRIS_No'] == int(data)]
        a = (result["term_found_matches"])
        value = result['Report']
        b = a.iloc[0]
        text = value.iloc[0]
        self.textEdit.setText(text)
        matches = []
        word = []
        for i in b.values():
            list_of_tuples = i[1]
            for item in list_of_tuples:
                matches.append(item)
        for key, value in b.items():
            term = [item[0] for item in value[1]]
            word.extend(term)
        
        indexed_matches = []

        ## NER
        doc = nlp_ner(text)
        for token in doc.ents:
            t1 = token.label_
            t2 = token.start_char
            t3 = token.end_char
            tm = (t1,t2,t3)
            indexed_matches.append(tm)
            word.append(t1)
        
        nlp = spacy.load("en_core_web_sm")
        doc2 = nlp(text)
        for token in doc2.ents:
            if(token.label_ == "QUANTITY"):
                t1 = token.label_
                t2 = token.start_char
                t3 = token.end_char
                tm = (t1,t2,t3)
                indexed_matches.append(tm)
                word.append(t1)
            else:
                pass

        colours = {}
        unique_words = list(set(word))
        for uw in unique_words:
            colours[uw] = None
        
        for w in unique_words:
            if w in colourdict:
                # If the word exists in the global dictionary, use its colour
                colours[w] = colourdict[w]
            else:
                # If the word doesn't exist, generate a random colour
                colours[w] = '#FFFF00'
                #print("It has got here")

        

        # Iterate through each match
        for wd, start, end in matches:
            # Initialize a variable to store the start index for each match
            current_start = 0
            # Find all occurrences of the word in the text
            while True:
                # Find the next occurrence of the word after the current_start index
                true_start = text.find(wd, current_start)
                # If no more occurrences are found, break out of the loop
                if true_start == -1:
                    break
                # Calculate the true end index based on the start index and word length
                true_end = true_start + len(wd)
                # Append the word and its true location to the indexed_matches list
                indexed_matches.append((wd, true_start, true_end))
                # Update the current_start index to search for the next occurrence
                current_start = true_start + 1
        #print(indexed_matches)
        indexed_matches = list(set(indexed_matches))
        indexed_matches = list(indexed_matches)
        print(indexed_matches)
        
        self.textEdit.setText(str(colours))
        options = {"ents": word, "colors": colours}
        ex = [{"text": text,
            "ents": [{"start": x[1], "end": x[2], "label": x[0].upper()} for x in indexed_matches]}]
        html = displacy.render(ex, style="ent", manual=True, options=options)
        self.textEdit.setHtml(html)

        # Add all matches to the matches combo box
        self.matchesCombo.clear()
        for line in unique_words:
            self.matchesCombo.addItem(line)
   
    def help_button_clicked(self):
        self.help = HelpWindow()
        self.help.show()

    def term_button_clicked(self):
        self.help = MeshWindow()
        self.help.show()
    
    def and_button_clicked(self):
        new_text = " AND "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def or_button_clicked(self):
        new_text = " OR "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def not_button_clicked(self):
        new_text = " NOT "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def except_button_clicked(self):
        new_text = " EXCEPT "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def custom_button_clicked(self):
        self.custom = CustomWindow()
        self.custom.show()

    def star_button_clicked(self):
        new_text = "* "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def q_button_clicked(self):
        new_text = "? "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def und_button_clicked(self):
        new_text = "_ "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)
    
    def quit_button_clicked(self):
        app.quit()

    def variables_button_clicked(self):
        self.variables = VariablesWindow()
        self.variables.show()

    def near_button_clicked(self):
        new_text = " NEAR "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def anonymise_changed(self, state):
        if state == 2:  # Checked state
            print("Checkbox checked")
           
        else:
            print("Checkbox unchecked")

    def export_button_clicked(self):
        """
        A function which executes when the export button is clicked
        Exports the selected row to the outputdata csv file, in its original format
        """
        selected_items = self.table_results.selectedIndexes()   # Retrieve selected data row index
        for index in selected_items:
            row = index.row()                                   # Retrieve the row of selected record
            column = index.column()                             # Retrieve column of the selected record
            if column != 0:                                     # If it isnt column zero, present an error
                self.index_error.exec()
                return
            else:    
                # Get the data of the selected cell and proceed
                data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)
        
        file_path = self.comboBox.currentText()                 # Obtain selected dataset
        df = pd.read_csv('data/'+file_path)                     # Convert it to a dataframe
        record = df[df['CRIS_No'] == int(data)]                 # Filter the dataframe by the CRIS_No
        df_data = clean_dataframe(record, ['Report'],           # Clean report column of whitespace
                            drop_duplicates=False,  
                            drop_nulls=True,        # Drop empty reports
                            drop_negatives=False,   
                            drop_ambiguous=False    
                            )
        
        # Export the row to outputdata.csv, appending it without the header or row index
        df_data.to_csv('data/outputdata.csv', mode='a', header = False, index=False)

    def colours_button_clicked(self):
        """
        A function which executes when the colours button is clicked
        Launches a dialogue window which allows a user to custom select the term matches
        """
        colour = QColorDialog.getColor(Qt.GlobalColor.black, None, "Select Color")
        if colour.isValid():
            print("Selected Color:", colour.name())
        word = self.matchesCombo.currentText()
        colourdict[word] = colour.name()

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
        df = pd.read_csv('data/synonyms.csv')
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

class CustomWindow(QtWidgets.QMainWindow, Ui_Custom):
    def __init__(self, *args, obj=None, **kwargs):
        super(CustomWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        init_errors(self)                                           # Initialise the error messages
        conn = sqlite3.connect("UserManagement.db")                 # Connect to the user management database
        c = conn.cursor()                                           # Setup a cursor, 'c'
        c.execute("SELECT * FROM searches")
        variables = c.fetchall()                                    # Select all values from database
        data = pd.DataFrame(variables, columns = ['Search'])
        self.model = TableModel(data)
        self.table_results.setModel(self.model)
        self.table_results.resizeColumnsToContents()
        self.but_create.clicked.connect(self.create_button_clicked) # Connect create button to function
        self.but_delete.clicked.connect(self.delete_button_clicked) # Connect delete button to function
        self.but_insert.clicked.connect(self.insert_button_clicked) # Connect insert button to function

    def create_button_clicked(self):
        """
        Function which gets called when the create button is pressed
        """ 
        query = self.lineEdit_query.text()           # Extract query from lineEdit
        response = self.proceed.exec()
        if response == QMessageBox.StandardButton.Yes:
            insert_search(query)
            self.close()
        else:
            self.lineEdit_query.clear()
            self.lineEdit_query.setFocus()  

    def delete_button_clicked(self):
        """
        Function which gets called when the delete button is pressed
        """ 
        selected_items = self.table_results.selectedIndexes()
        # Iterate over the selected indexes
        for index in selected_items:
            data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)      
        
        response = self.proceed.exec()
        if response == QMessageBox.StandardButton.Yes:
            remove_search(data)
            self.close()
        else:
            self.lineEdit_query.clear()
            self.lineEdit_query.setFocus()  

    def insert_button_clicked(self):
        """
        Function which gets called when the copy button is pressed
        """ 
        selected_items = self.table_results.selectedIndexes()
        # Iterate over the selected indexes
        for index in selected_items:
            data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)
        clipboard = QApplication.clipboard()
        clipboard.setText(data)
        self.close()
                 
class VariablesWindow(QtWidgets.QMainWindow, Ui_Variables):
    """
    A window which launches after the variables button is clicked
    A basic window with a table of preset variables
    Additional feature to add a custom variable
    """
    def __init__(self, *args, obj=None, **kwargs):
        """
        Function to inistialise the variables window
        """
        super(VariablesWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)                                          # Setup UI
        self.but_create.clicked.connect(self.create_button_clicked) # Connect create button to function
        self.but_delete.clicked.connect(self.delete_button_clicked) # Connect delete button to function
        init_errors(self)                                           # Initialise the error messages
        conn = sqlite3.connect("UserManagement.db")                 # Connect to the user management database
        c = conn.cursor()                                           # Setup a cursor, 'c'
        c.execute("SELECT * FROM variables")
        variables = c.fetchall()                                    # Select all values from database
        data = pd.DataFrame(variables, columns = ['Variable Name', 'Query'])
        self.model = TableModel(data)
        self.table_results.setModel(self.model)
        self.table_results.resizeColumnsToContents()
                                                  
    def create_button_clicked(self):
        """
        Function which gets called when the create button is pressed
        """
        variable = self.lineEdit_var.text()          # Extract variable from lineEdit   
        query = self.lineEdit_query.text()           # Extract query from lineEdit
        response = self.proceed.exec()
        if response == QMessageBox.StandardButton.Yes:
            insert_variable(variable, query)
            self.close()
        else:
            self.lineEdit_var.clear()
            self.lineEdit_query.clear()           
            self.lineEdit_var.setFocus()

    def delete_button_clicked(self):
        """
        Function which gets called when the create button is pressed
        """
        selected_items = self.table_results.selectedIndexes()
        # Iterate over the selected indexes
        for index in selected_items:
            data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)      
        response = self.proceed.exec()
        if response == QMessageBox.StandardButton.Yes:
            remove_variable(data)
            self.close()
        else:
            self.lineEdit_query.clear()
            self.lineEdit_query.setFocus() 

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
try:
    if login_success == 1:
        window = MainWindow()
        window.show()
        app.exec()
except:
    app.quit()



