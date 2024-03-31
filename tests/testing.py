import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
import spacy
from spacy import displacy
import json
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple PyQt6 Program")
        self.setGeometry(100, 100, 500, 500)  # Set window geometry (x, y, width, height)

        self.text_edit = QTextEdit(self)  # Create QTextEdit widget
        self.text_edit.setGeometry(50, 50, 400, 400)  # Set text edit geometry (x, y, width, height)

        nlp_ner = spacy.load("model-best")
        newtext = "HIV is bad unless treated with loperamide. HIV is even worse than Corona Virus. Headaches, or even worse, penicillin"
        doc = nlp_ner(newtext)
        colors = {"PATHOGEN": "#F67DE3", "MEDICINE": "#7DF6D9", "MEDICALCONDITION":"#a6e22d"}
        options = {"colors": colors} 
        newhtml = displacy.render(doc, style="ent", options= options)
        #self.text_edit.setText(newtext)
        #self.text_edit.setHtml(newhtml)

        nlp = spacy.load("en_core_web_sm")

        # Input text
        text = "The temperature is 25 degrees Celsius. It's 3cm by 3cm, or even better, 4cm x 4cm. 25 grams of dosage, which is 50 metres which is a lot"

        # Process the text
        doc = nlp(text)

        # Extract measurements
        html = displacy.render(doc, style="ent")

        self.text_edit.setText(text)
        self.text_edit.setHtml(html)

def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()