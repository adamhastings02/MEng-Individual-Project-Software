"""
---------------------------------------------------------------------------------
Program: RADEX Tool
By: Adam Hastings
Date: 01/11/2023 - 14/05/2024
For: ELEC5870M - MEng Individual Project
---------------------------------------------------------------------------------
Description:
---------------------------------------------------------------------------------
This program presents a radiology report data extraction tool
Rapidly scan datasets to highlight key information 
Use this information to decide on future treatment for each anonymised patient
GUI to operate the system, all instructions on usage can be found in help window
--------------------------------------------------------------------------------- 
"""
# General Imports:
import sys
import re
import spacy
import string
from spacy import displacy
from time import sleep
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
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
from guis.mesh_ui import Ui_Mesh
from guis.variables_ui import Ui_Variables
from guis.custom_ui import Ui_Custom
# RADEX Tool Imports:
from nlprules.preprocessing import clean_dataframe, remove_stopwords, remove_negated_phrases
from nlprules.radexpressions import evaluate_regex, get_regex_proximity, get_regex_wildcards, string_search
from nlprules.dfsearch import check_all_matches, search_dataframe, evaluate_sentences, list_to_string
from nlprules.expression import Expression
# Globals declaration list:
global colourdict           # A dictionary to store the custom colour choices of the user
colourdict = {"PATHOGEN": "#F67DE3", "MEDICINE": "#7DF6D9", "MEDICALCONDITION":"#a6e22d", "QUANTITY":"#ffffff"}
global elapsed_times        # A list to contain the elapsed times of searches for performance analysis
elapsed_times = []
global lengths_times        # A list to contain the times of expand record based on number of words in transcription
lengths_times = []
global search_times         # A list to contain the time taken to perform a search based on number of words in search
search_times = []
global approved             # A list to store any records that are approved
approved = []
global rejected             # A list to store any records that are rejected
rejected = []
preprocess = (True, True, True, True)   # A tuple containing the user preferences of preprocessing (defaults to True)

# Useful Commands:
# pyuic6 mainwindow.ui -o MainWindow.py
# pipenv shell
# python main.py
# pyinstaller --onefile main.py
# To export as an executable, type the above command, and copy across the folders from
# this entire directory

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
    self.indicator_led.setValue(0)                      # Turn off LED indicator


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

    # Error for invalid search
    self.invalid_error = QMessageBox()
    self.invalid_error.setIcon(QMessageBox.Icon.Critical)
    self.invalid_error.setWindowTitle('Error')
    self.invalid_error.setText('Search Failed. Please try again')

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
                            drop_duplicates=preprocess[0], # drop duplicate entries // CHANGE
                            drop_nulls=preprocess[1], # drop empty reports
                            drop_negatives=preprocess[2], # remove negated phrases
                            drop_ambiguous=preprocess[3] # remove phrases with ambiguous negation
                            )

    #STOP-WORD REMOVAL
    stop_words = pd.read_csv('data/stopwords.csv').T.values[0]
    df_data2 = remove_stopwords(df_data, [column_report]) # This rem5oves stopwords
    
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

def remove_unwanted_terms(lst):
    """
    Removes unwanted values from a list

    Args:
        lst: The list you wish to scan for unwanted items

    Returns:
        result: The list containing the unwanted terms
    """
    result = []
    for item in lst:
        if isinstance(item, list):
            result.append(remove_unwanted_terms(item))  # Recursively process nested lists
        elif isinstance(item, str) and len(item) == 1 and item in string.punctuation:
            continue  # Skip single punctuation terms
        elif item == '¬':
            continue  # Skip specific unwanted character
        else:
            result.append(item)
    return result

def count_terms(lst):
    """
    Counts the number of terms in a nested list

    Args:
        lst: The nested list you wish to count how many items are in

    Returns:
        count: An integer representing the number of terms
    """
    count = 0
    for item in lst:
        if isinstance(item, list):
            count += count_terms(item)  # Recursively count terms in nested lists
        else:
            count += 1
    return count

def convert_date(date):
    """
    Converts dates from MM/DD/YYYY to DD/MM/YYYY using regular expressions \n
    Only works if ..//XX/.. 13 <= XX <= 31, otherwise its treated as correct \n
    Otherwise there is encouragement elsewhere to ensure all dates are in UK format, not americanised

    Args:
        date: The input date, to check if it is americanised

    Returns:
        data: The output date, which is either the same if in UK format or converted if middle value is between 13 and 31 inclusive
    """
    # Regular expression to match MM/DD/YYYY format
    mm_dd_yyyy_pattern = r'(\d{2})/(\d{2})/(\d{4})'
    # Check if the date matches MM/DD/YYYY format
    if re.match(mm_dd_yyyy_pattern, date):
        # If it matches, extract month, day, and year
        month, day, year = re.match(mm_dd_yyyy_pattern, date).groups()
        # Check if the day part is between 13 and 31
        if 13 <= int(day) <= 31:
            # Return the date in DD/MM/YYYY format
            return f'{day}/{month}/{year}'
    # If the date does not match the condition, return as is
    return date

class TableModel(QtCore.QAbstractTableModel):
    """
    A class which enables a table to be instantiated
    """
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        # Return data
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)   

    def rowCount(self, index):
        # Return the row count
        return self._data.shape[0] 

    def columnCount(self, index):
        # Return the column count
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # Set the data for the column headers. Section is the index of the column/row.
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
        """
        A function which initialises the main window and sets up function connections
        """
        super(MainWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)                                                  # Setup UI
        self.showMaximized()                                                # Maximise the window
        self.setStyleSheet("background-color: #F5F5DC;")                    # Set beige background
        self.table_results.setStyleSheet("background-color: #F5F5DC;")      # Set beige stylesheet
        self.but_manual.clicked.connect(self.manual_button_clicked)         # Connect search button to function
        self.but_clear.clicked.connect(self.clear_button_clicked)           # Connect clear button to function
        self.but_expand.clicked.connect(self.expand_button_clicked)         # Connect expand record button to function
        self.but_help.clicked.connect(self.help_button_clicked)             # Connect help button to window
        self.but_termfind.clicked.connect(self.term_button_clicked)         # Connect termfinder button to window
        self.but_and.clicked.connect(self.and_button_clicked)               # Connect and button to function
        self.but_variables.clicked.connect(self.variables_button_clicked)   # Connect variables button to window
        self.but_or.clicked.connect(self.or_button_clicked)                 # Connect or button to function
        self.but_not.clicked.connect(self.not_button_clicked)               # Connect not button to function
        self.but_except.clicked.connect(self.except_button_clicked)         # Connect except button to function
        self.but_custom.clicked.connect(self.custom_button_clicked)         # Connect custom button to window
        self.but_star.clicked.connect(self.star_button_clicked)             # Connect asteriks button to function
        self.but_q.clicked.connect(self.q_button_clicked)                   # Connect question mark button to function
        self.but_und.clicked.connect(self.und_button_clicked)               # Connect underscore button to function
        self.but_quit.clicked.connect(self.quit_button_clicked)             # Connect quit button to function
        self.but_near.clicked.connect(self.near_button_clicked)             # Connect near button to function
        self.but_export.clicked.connect(self.export_button_clicked)         # Connect export button to function
        self.but_colours.clicked.connect(self.colours_button_clicked)       # Connect colour select button to function
        self.but_performance.clicked.connect(self.performance_button_clicked)# Connect performance button to function
        self.but_approve.clicked.connect(self.approve_button_clicked)       # Connect approve button to function
        self.but_decline.clicked.connect(self.decline_button_clicked)       # Connect decline button to function
        self.but_searchall.clicked.connect(self.searchall_button_clicked)   # Connect search all false button to function
        self.but_original.clicked.connect(self.original_button_clicked)     # Connect view original button to function
        self.but_filtering.clicked.connect(self.preview_button_clicked)     # Connect preview button to function
        self.but_prepro.clicked.connect(self.preprocess_button_clicked)     # Connect preprocessing options button to qdialog
        self.dateEdit.setDate(QDate.currentDate())                          # Set the date edit as the current date
        
        init_errors(self)                                                   # Initialise the error message boxes

    def manual_button_clicked(self):
        """
        A function which executes when the search button near the manual entry line is clicked
        """
        start_time = time.time()
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

        # Convert any dates that are in American Format
        data['Events_date'] = data['Events_date'].apply(convert_date)   # Convert event date
        data['DOB'] = data['DOB'].apply(convert_date)                   # Convert DOB

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
        try:
            results = df_search(data, result)   # Search the dataframe
        except ValueError:
            self.invalid_error.exec()   # Display an error if theres an invalid search instead of crashing
            return
        condition = results['term_found'] == True   # Filter dataframe by matching records
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
            self.model = TableModel(filtered_df)    # If a record/s exist, populate the table with them
            self.table_results.setModel(self.model)
            self.table_results.resizeColumnsToContents()    # Resize table to match 
        else:
            self.nothing_error.exec() # Executes if no results for searched expression
        
        # Store time to search value 
        end_time = time.time()                          # Stop timer
        elapsed_time = end_time-start_time              # Determine elapsed time
        num_rows = len(data)                            # Determine number of records
        search_times.append((num_rows, elapsed_time))   # Append this data to search times dict (global)
     
    def clear_button_clicked(self):
        """
        A function which executes when the search button near the clear all button is clicked
        """
        box_clear(self)

    def expand_button_clicked(self):
        """
        A function which executes when the expand record button is clicked \n
        Puts the transcription of the record in the textEdit \n
        Highlights the records using RegEx and NER
        """
        start_time = time.time()                                # Start a timer
        selected_items = self.table_results.selectedIndexes()   # Get the row number index
        selected_dataset = self.comboBox.currentText()          # Get the selected dataset
        nlp_ner = spacy.load("model-best")                      # Load the NER model
        # Iterate over the selected indexes
        for index in selected_items:
            row = index.row()                                   # Retrieve the row of selected record
            column = index.column()                             # Retrieve column of the selected record
            if column != 0:                                     # If it isnt column zero, present an error
                self.index_error.exec()
                return
            else:    
                # Get the data of the selected cell and proceed
                data = self.table_results.model().data(index, role=Qt.ItemDataRole.DisplayRole)
        
        # Find the transcription matching the description
        df = data_retrieval(selected_dataset)                       # Retreive the dataset
        man = self.ent_manual.toPlainText()                         # Convert search bar to plaintext
        conn = sqlite3.connect("UserManagement.db")                 # Connect to the user management database
        c = conn.cursor()                                           # Setup a cursor, 'c'
        c.execute("SELECT * FROM variables")
        variables = c.fetchall()                                    # Select all values from database
        for var, text in variables:                                 # If any variables occur in the search,
            man = man.replace(var, text)                            # Assign them to their true value

        if man.strip() == "":                                       # If search bar is empty, throw an error
            self.manual_error.exec()
            return
        else:    
            expr = Expression()                                     # Generate an expression object
            result = expr.parse_string(man)                         # Parse the search bar to an expression
        
        # Search the results and filter the dataframe by values which are true under the expression
        results = df_search(df, result)                             
        result = results[results['CRIS_No'] == int(data)]           
        a = (result["term_found_matches"])                          
        value = result['Report']
        processed = value
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
        indexed_matches = list(set(indexed_matches))
        indexed_matches = list(indexed_matches)
        
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
        
        # End timer and extract total time elapsed
        # No of terms vs time
        num = (expr.parse_string(man))
        cleaned_list = remove_unwanted_terms(num)
        num_terms = count_terms(cleaned_list)
        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_times.append((num_terms, elapsed_time))

        # Length of record vs time
        words = text.split()
        num_words = len(words)
        lengths_times.append((num_words,elapsed_time))

        # Alight the certainty LED
        selected_items = self.table_results.selectedIndexes()
        selected_dataset = self.comboBox.currentText()
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
        file_path = selected_dataset
        df_data0 = pd.read_csv('data/'+file_path)
        df_data0.fillna('', inplace=True)
        
        result = expr.parse_string(man)
        barry = result
        results = df_search(df_data0, result)                             
        result = results[results['CRIS_No'] == int(data)]           
        a = (result["term_found_matches"])                          
        value = result['Report']
        b = a.iloc[0]
        text = value.iloc[0]
        matches = []
        word = []
        for i in b.values():
            list_of_tuples = i[1]
            for item in list_of_tuples:
                matches.append(item)
        for key, value in b.items():
            term = [item[0] for item in value[1]]
            word.extend(term)
        unique_words = list(set(word))
        flag = 0
        x2 = processed.iloc[0]
        if preprocess[2] == True:
            for x3 in unique_words:
                if x3 not in text and x3 not in x2:
                    flag = 0
                    break
                elif x3 in text and x3 not in x2:
                    flag = 1
                    break
                elif x3 in text:
                    try:
                        idx = text.split().index(x3)  # Find the index of x3 in text
                        if idx >= 3:
                            words_before = text.split()[idx - 3:idx]
                            # Check if any word is 'no' or 'No'
                            if any(word.lower() == 'no' for word in words_before):
                                flag = 2
                                break
                    except ValueError:
                        flag = 2                     
        if flag == 1:
            self.indicator_led.setValue(100)
            self.indicator_led.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif flag == 2:
            self.indicator_led.setValue(100)
            self.indicator_led.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.indicator_led.setValue(100)
            self.indicator_led.setStyleSheet("QProgressBar::chunk { background-color: green; }")      
   
    def help_button_clicked(self):
        self.help = HelpWindow()
        self.help.show()

    def term_button_clicked(self):
        self.help = MeshWindow()
        self.help.show()
    
    def and_button_clicked(self):
        """
        A function which adds the AND expression to the search bar
        """
        new_text = " AND "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def or_button_clicked(self):
        """
        A function which adds the OR expression to the search bar
        """
        new_text = " OR "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def not_button_clicked(self):
        """
        A function which adds the NOT expression to the search bar
        """
        new_text = " NOT "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def except_button_clicked(self):
        """
        A function which adds the NOT expression to the search bar
        """
        new_text = " EXCEPT "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def custom_button_clicked(self):
        """
        A function which opens up the custom searches window
        """
        self.custom = CustomWindow()
        self.custom.show()

    def star_button_clicked(self):
        """
        A function which adds the * wildcard to the search bar
        """
        new_text = "* "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def q_button_clicked(self):
        """
        A function which adds the ? wildcard to the search bar
        """
        new_text = "? "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

    def und_button_clicked(self):
        """
        A function which adds the _ wildcard to the search bar
        """
        new_text = "_ "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)
    
    def quit_button_clicked(self):
        """
        A function which quits the program
        """
        app.quit()

    def variables_button_clicked(self):
        """
        A function which opens the variables viewer window
        """
        self.variables = VariablesWindow()
        self.variables.show()

    def near_button_clicked(self):
        """
        A function which adds the NEAR expression to the search bar
        """
        new_text = " NEAR "
        current_text = self.ent_manual.toPlainText()
        updated_text = current_text + new_text
        self.ent_manual.setPlainText(updated_text)

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
        approval_status_value = ['Unlabelled']
        df_data['Approval_status'] = approval_status_value
        df_data.to_csv('data/outputdata.csv', mode='a', header = False, index=False)

    def colours_button_clicked(self):
        """
        A function which executes when the colours button is clicked
        Launches a dialogue window which allows a user to custom select the term matches
        """
        colour = QColorDialog.getColor(Qt.GlobalColor.black, None, "Select Color")
        if colour.isValid():
            print("Selected Color:", colour.name())
        word = self.matchesCombo.currentText()              # Extract the word needing to be highlighted
        colourdict[word] = colour.name()                    # Permanently assign the new selected colour to that term

    def performance_button_clicked(self):
        """
        A function which executes when the performance button is clicked \n
        Plots various performance related metrics \n
        This includes: 
            - Number of Searches vs Elapsed Time of Expand (Bar)
            - Number of Words in Report vs Elapsed Time of Expand (Scatter)
            - Average search time (Display)
            - Accuracy of searches based on approves and declines (Pie)
        """
        # 1st graph
        # Convert the list of tuples to a NumPy array
        data_array = np.array(elapsed_times)
        # Calculate the average of the second value for each unique first value
        averages = []
        for unique_first_value in np.unique(data_array[:, 0]):
            subset = data_array[data_array[:, 0] == unique_first_value]
            average = np.mean(subset[:, 1])
            averages.append((unique_first_value, average))
        # Separate the unique first values and their corresponding averages
        x_values, y_values = zip(*averages)
        # Plot the averages
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        ax1.bar(x_values, y_values)
        ax1.set_xlabel('Number of terms')
        ax1.set_ylabel('Average time taken for record expansion (s)')
        ax1.set_title('Plot Of Average Time Taken For Record Expansion vs Number Of Search Terms Used')
        for x, y in zip(x_values, y_values):
            ax1.text(x, y, f'{y:.2f}', ha='center', va='bottom')

        # 2nd Graph 
        x_values = [item[0] for item in lengths_times]
        y_values = [item[1] for item in lengths_times]
        # Plot the data
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)
        ax2.scatter(x_values, y_values, color='b', label='Data')
        coefficients_1 = np.polyfit(x_values, y_values, 1)  # Fit a first-degree polynomial (line)
        poly_1 = np.poly1d(coefficients_1)
        ax2.plot(np.unique(x_values), poly_1(np.unique(x_values)), color='r', label='Average')
        # Add labels and title
        ax2.set_xlabel('Number of words in report transcript')
        ax2.set_ylabel('Time taken for record expansion (s)')
        ax2.set_title('Plot Of Average Time Taken For Record Expansion vs Number Of Words in Record Transcription')
        # Show the plot
        ax2.grid(True)
        ax2.legend()

        # 3rd Graph
        message_box = QMessageBox()
        message_box.setWindowTitle('Average Search Time')
        num_records = [item[0] for item in search_times]
        second_numbers = [item[1] for item in search_times]
        avg_time = np.mean(second_numbers)
        message_box.setText(f"Number of records: {num_records[0]} \nAverage time taken: {avg_time:.2f} seconds")
        message_box.exec()  # Show a textbox containing the number of records and the average search time in a:bc seconds format

        # 4th Graph
        sizes = [len(approved), len(rejected)]  # Determine number of approves and declines
        labels = ['Correct', 'Incorrect']       # Labels for the categories
        colours = ['green', 'red']              # Colours for the categories
        total_records = sum(sizes)
        # Plot
        fig3 = plt.figure()
        ax3 = fig3.add_subplot(111)
        ax3.pie(sizes, labels=labels, colors=colours, autopct='%1.1f%%', startangle=140)
        term = self.ent_manual.toPlainText()
        ax3.set_title(f"Search accuracy for: {term}")
        ax3.text(-1, -1.25, f'Total Records: {total_records}', fontsize=12, color='black', ha='center')
        plt.show()

    def approve_button_clicked(self):
        """
        A function which executes when the approve button is clicked \n
        Approves the highlighted record, stores it in a dictionary and outputs it to the excel plugin
        """
        selected_items = self.table_results.selectedIndexes()
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
        if data not in approved and data not in rejected:
            approved.append(data)
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
            approval_status_value = ['Approved']
            df_data['Approval_status'] = approval_status_value
            df_data.to_csv('data/outputdata.csv', mode='a', header = False, index=False)
        else:
            pass

    def decline_button_clicked(self):
        """
        A function which executes when the decline button is clicked \n
        Declines the highlighted record, stores it in a dictionary and outputs it to the excel plugin
        """
        selected_items = self.table_results.selectedIndexes()
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
        if data not in rejected and data not in approved:
            rejected.append(data)
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
            approval_status_value = ['Declined']
            df_data['Approval_status'] = approval_status_value
            df_data.to_csv('data/outputdata.csv', mode='a', header = False, index=False)
        else:
            pass
    
    def searchall_button_clicked(self):
        """
        A function which executes when the search all button is clicked \n
        Searches for all false occurences of the search, where the terms havent occured
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

        # Convert any dates that are in American Format
        data['Events_date'] = data['Events_date'].apply(convert_date)   # Convert event date
        data['DOB'] = data['DOB'].apply(convert_date)                   # Convert DOB

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
        condition = results['term_found'] == False
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

    def original_button_clicked(self):
        """
        A function which executes when the view original button is clicked \n
        Presents a textbox containing the original, unedited and unhighlighted record
        """
        selected_items = self.table_results.selectedIndexes()
        selected_dataset = self.comboBox.currentText()
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
        file_path = selected_dataset
        df_data0 = pd.read_csv('data/'+file_path)
        df_data0.fillna('', inplace=True)
        result = df_data0[df_data0['CRIS_No'] == int(data)]
        value = result['Report']
        message_box = QMessageBox()
        message_box.setWindowTitle('Original Report')
        message_box.setText(str(value.iloc[0]))
        message_box.exec()

    def preview_button_clicked(self):
        """
        A function which executes when the preview button is clicked \n
        Presents the head (top 5) records of the dataframe selected in the combo box
        """
        selected_dataset = self.comboBox.currentText()
        if selected_dataset == "Select":
            self.dataset_error.exec()               # Error popup for no dataset selected
            return                                  # End function
        else:
            data = data_retrieval(selected_dataset) # Retrieve the dataset
        head = data.head()
        self.model = TableModel(head)
        self.table_results.setModel(self.model)
        self.table_results.resizeColumnsToContents()
    
    def preprocess_button_clicked(self):
        """
        A function which executes when the preprocessing options button is clicked \n
        Presents a Qdialog where the user can custom select which preprocessing options they want (defaults all to True)
        """
        dialog = PreprocessCheckbox()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pres = dialog.get_checkbox_values()
            global preprocess
            preprocess = pres
            
class HelpWindow(QtWidgets.QMainWindow, Ui_Help):
    """
    This window appears after the 'Help' button is clicked.
    Contains instructions for the user if they need assistance
    """
    def __init__(self, *args, obj=None, **kwargs):
        # Initialise the window
        super(HelpWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.but_close.clicked.connect(self.close_button_clicked)
        self.showMaximized()
    
    def close_button_clicked(self):
        # Button to close the window
        self.close()

class MeshWindow(QtWidgets.QMainWindow, Ui_Mesh):
    """
    This window appears after the 'Term Finder' button is clicked.
    A MeSH searching window appears, where the user can search for related terms
    """
    def __init__(self, *args, obj=None, **kwargs):
        # Initialise the window
        super(MeshWindow, self).__init__(*args, **kwargs) 
        self.setupUi(self)
        self.but_search.clicked.connect(self.search_clicked)
        self.but_close.clicked.connect(self.close_clicked)
        init_errors(self)
    
    def search_clicked(self):
        # Search for related terms
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
        self.model = TableModel(data)                               # Assign these values to the table
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
            insert_search(query)                     # Add query to the database
            self.close()
        else:
            self.lineEdit_query.clear()              # Clears the text entry to start again 
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
            remove_search(data)                     # Removes the selected search for the custom list
            self.close()
        else:
            self.lineEdit_query.clear()             # Clears the text entry to start again
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
        clipboard.setText(data)                     # Copy custom search to clipboard
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
            insert_variable(variable, query)        # Insert variable with its query into database
            self.close()
        else:
            self.lineEdit_var.clear()               # Clear entry boxes and try again
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
            remove_variable(data)                   # Removes selected variable from the database
            self.close()
        else:
            self.lineEdit_query.clear()             # Clear entry boxes and try again
            self.lineEdit_query.setFocus() 

class PreprocessCheckbox(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Checkbox Popup')
        layout = QVBoxLayout()  # Create layout

        # Create checkboxes, with preprocessing options and default as checked
        self.checkbox1 = QCheckBox('Drop Duplicates')
        self.checkbox1.setChecked(True)
        self.checkbox2 = QCheckBox('Drop Nulls')
        self.checkbox2.setChecked(True)
        self.checkbox3 = QCheckBox('Drop Negatives')
        self.checkbox3.setChecked(True)
        self.checkbox4 = QCheckBox('Drop Ambiguous')
        self.checkbox4.setChecked(True)

        # Add checkboxes to layout
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.checkbox3)
        layout.addWidget(self.checkbox4)

        # Add OK button
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.close_popup)
        layout.addWidget(self.ok_button)

        # Set layout
        self.setLayout(layout)

    def close_popup(self):
        # Emit accepted signal and close dialog
        self.accept()

    def get_checkbox_values(self):
        # Return checkbox values
        return (
            self.checkbox1.isChecked(),
            self.checkbox2.isChecked(),
            self.checkbox3.isChecked(),
            self.checkbox4.isChecked()
        )

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
