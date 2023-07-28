from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPalette, QColor
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("Main Window")

        # Create a main layout
        self.main_layout = QVBoxLayout()

        # Create a widget to hold the main layout
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        # Add the "IP 연결" label
        self.label = QLabel("IP 연결")
        self.label.setStyleSheet('height:30px')
        self.main_layout.addWidget(self.label)

        # Create the IP input box and the connect button
        ip_input_line = QHBoxLayout()
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("IP 주소 입력")
        self.connect_button = QPushButton()
        self.connect_button.setText('연결')

        self.connect_button.clicked.connect(self.on_connect_button_clicked)
        ip_input_line.addWidget(self.ip_input)
        ip_input_line.addWidget(self.connect_button)

        # Add the IP input box and the connect button to the main layout
        self.main_layout.addLayout(ip_input_line)

        # Create another vertical layout and add it to the main layout
        self.extra_layout = QVBoxLayout()

        self.main_layout.addLayout(self.extra_layout)

        # Set the main widget as the central widget of the window
        self.setCentralWidget(self.main_widget)

    def on_connect_button_clicked(self):
        print('연결')

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
