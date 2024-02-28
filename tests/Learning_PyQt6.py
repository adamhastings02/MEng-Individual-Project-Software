# Local imports
import sys
from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor, QFont
from PyQt6.QtCore import Qt

# pyuic6 mainwindow.ui -o MainWindow.py
# pipenv shell
# python Learning_PyQt6.py

# Custom Methods
# self.pushButton.clicked.connect(self.the_button_was_clicked)
from guis.MainWindow import Ui_MainWindow
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from nlprules.preprocessing import clean_dataframe, remove_stopwords, remove_negated_phrases
from nlprules.radexpressions import evaluate_regex, get_regex_proximity, get_regex_wildcards, string_search
from nlprules.dfsearch import check_all_matches, search_dataframe, evaluate_sentences, list_to_string
from nlprules.expression import Expression

# Local imports
file_path = 'beers.csv'
df_data0 = pd.read_csv(file_path)
df_data0.fillna('', inplace=True)
len(df_data0)

column_report = 'Review'
column_history = 'history'
column_label = 'label'

#RAW DATA
with pd.option_context('display.max_colwidth', None):
    print(df_data0.head())
    print('\n')

#CLEANED DATA
df_data = clean_dataframe(df_data0, [column_report], 
                          drop_duplicates=True, # drop duplicate entries
                          drop_nulls=True, # drop empty reports
                          drop_negatives=True, # remove negated phrases
                          drop_ambiguous=True # remove phrases with ambiguous negation
                          )
with pd.option_context('display.max_colwidth', None):
    print(df_data.head())
    print('\n')  

#STOP-WORD REMOVAL
stop_words = pd.read_csv('data/stopwords.csv').T.values[0]
df_data2 = remove_stopwords(df_data, [column_report]) # This removes stopwords
with pd.option_context('display.max_colwidth', None):
    print(df_data2.head())
    print('\n')  


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])
    
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.showMaximized()
        self.setStyleSheet("background-color: #F5F5DC;")
        self.tableView_2.setStyleSheet("background-color: #F5F5DC;")
        self.pushButton.clicked.connect(self.the_button_was_clicked)
        
        data2 = list(df_data0.to_records(index=False))
        self.model2 = TableModel(data2)
        self.tableView_2.setModel(self.model2)
        self.tableView_2.resizeColumnsToContents()
    
    def the_button_was_clicked(self):
        selected_beer = self.comboBox.currentText()
        if selected_beer != "Any":
            beer = [selected_beer]
            result = df_data0[df_data0['Beer Name'].isin(beer)].iloc[0, 1]
            self.textEdit.setText(result)
            self.textEdit.adjustSize()
            selected_adj = self.lineEdit.text()
            plain_text = self.textEdit.toPlainText()
            if selected_adj in result:
                formatted_text = plain_text.replace(selected_adj, f"<b>{selected_adj}</b>")
                self.textEdit.setHtml(formatted_text)
            else:
                words = (selected_beer + " is not " + selected_adj)
                self.textEdit.setText(words)

        else:
            selected_adj = self.lineEdit.text()
            filtered_df = df_data0[df_data0['Review'].str.contains(selected_adj, case=False)]
            if len(filtered_df != 0):
                print(filtered_df)
                data = list(filtered_df.to_records(index=False))
                self.model = TableModel(data)
                self.tableView.setModel(self.model)
                self.tableView.resizeColumnsToContents()
            else:
                self.tableView.clearSelection()
                self.tableView.resizeColumnsToContents()
    def answer_retrieval(self):
        """
        A function to extract all the values from the assisted expression entering system. Takes all 4 rows and columns of values and transforms
        them into a nested list of boolean operators and search terms 

        Returns:
        result (Nested list) - The nested list of the entered terms, wildcards, booleans and proximity values, cleaned of all empty values and
        ready to be used for a string search
        """
        # Retrieve the term column
        term1 = self.ent_term1.text()
        term2 = self.ent_term2.text()
        term3 = self.ent_term3.text()
        term4 = self.ent_term4.text()
        
        # Retrieve the wildcard column
        wild1 = self.ent_wild1.currentText()
        wild2 = self.ent_wild2.currentText()
        wild3 = self.ent_wild3.currentText()
        wild4 = self.ent_wild4.currentText()

        # Retrieve the boolean expression column
        expr1 = self.ent_expr1.currentText()
        expr2 = self.ent_expr2.currentText()
        expr3 = self.ent_expr3.currentText()

        # Retrieve the proximity column
        prox1 = self.spin_prox1.value()
        prox2 = self.spin_prox2.value()
        prox3 = self.spin_prox3.value()

        # Place all these values in an ordered list, remove null values and 0s, and set the list values as a string
        expression = [term1, wild1, expr1, prox1, term2, wild2, expr2, prox2, term3, wild3, expr3, prox3, term4, wild4]
        filtered_expression = [x for x in expression if x != 0 and x != '' and x != 'None']
        string_list = [str(item) for item in filtered_expression]

        # Convert the list of strings to a format which can work with the parse_string function
        concatenated_list = []
        current_item = ''
        for j in string_list:
            if j.isalpha() or '~' in j:
                # If the item is a letter, append it directly to the result list
                current_item = j
                concatenated_list.append(j)
            else:
                # If the item is not a letter, concatenate it to the previous item (if any)
                if current_item:
                    current_item += j
                    concatenated_list[-1] = current_item

        # Convert this list of strings to a string, then use parse_string for usability in string searching
        final_string = list_to_string(concatenated_list)
        expr = Expression()
        result = expr.parse_string(final_string)
        return result           
            
     
        

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()


