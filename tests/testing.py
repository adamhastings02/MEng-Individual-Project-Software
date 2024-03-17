import spacy
from spacy import displacy
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PyQt6 Program")
        self.setGeometry(100, 100, 500, 500)  # Set window geometry (x, y, width, height)

        ############# INSERT TEST CODE HERE ############
        self.text_edit = QTextEdit(self)  # Create QTextEdit widget
        self.text_edit.setGeometry(50, 50, 400, 400)  # Set text edit geometry (x, y, width, height)
        doc_text = "A common human skin tumour is caused by activating mutations in beta-catenin." 
        self.text_edit.setText(doc_text)                              #y y                        
        start_end_labels = [[15, 26, "disease"], [64, 76, "protein"]] #y
        colors = {"DISEASE": "green",                                 #y
                "PROTEIN": "orange"
                }
        options = {"ents": ["DISEASE", "PROTEIN"], "colors": colors}
        ex = [{"text": doc_text,
            "ents": [{"start": x[0], "end": x[1], "label": x[2]} for x in start_end_labels]}]
        html = displacy.render(ex, style="ent", manual=True, options=options)
        self.text_edit.setHtml(html)

def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
