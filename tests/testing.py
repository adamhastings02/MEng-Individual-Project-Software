from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QProgressBar, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Bar Color")
        self.setGeometry(100, 100, 400, 200)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create buttons
        self.green_button = QPushButton("Green", self)
        self.green_button.clicked.connect(self.set_progress_green)
        layout.addWidget(self.green_button)

        self.red_button = QPushButton("Red", self)
        self.red_button.clicked.connect(self.set_progress_red)
        layout.addWidget(self.red_button)

        # Create a progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

    def set_progress_green(self):
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")

    def set_progress_red(self):
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()