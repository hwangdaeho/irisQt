from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QToolButton
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize
class GuideScreen(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        main_layout = QVBoxLayout(self)  # Main layout

        center_widget = QWidget()  # Widget for center alignment
        center_layout = QVBoxLayout(center_widget)  # Layout for center alignment
        center_layout.setContentsMargins(0, 0, 0, 0)  # Set layout margins to 0

        # Guide image
        self.label = QLabel(self)
        self.image = QPixmap(':image/Step1.jpg')
        self.label.setPixmap(self.image)
        self.label.setAlignment(Qt.AlignCenter)

        # Button to go back to ImageMain screen
        self.button = QPushButton("다음", self)
        self.button.setStyleSheet('background-color: #B50039; border: none; color: white; font-size:15px')
        self.button.clicked.connect(lambda: main_window.load_screen_from_path('screen/calibration/step/step2.py', 'GuideScreen2'))

        self.button.setFixedSize(QSize(180, 48))  # Set fixed size for the button

        center_layout.addWidget(self.label, alignment=Qt.AlignCenter)  # Add image label to the center layout
        center_layout.addWidget(self.button, alignment=Qt.AlignCenter)  # Add button to the center layout

        main_layout.addStretch(1)  # Add stretchable space
        main_layout.addWidget(center_widget)  # Add center widget to the main layout
        main_layout.addStretch(1)  # Add stretchable space
