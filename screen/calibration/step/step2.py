from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QToolButton
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize

class GuideScreen2(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()

        main_layout = QVBoxLayout(self)  # Main layout

        center_widget = QWidget()  # Widget for center alignment
        center_layout = QVBoxLayout(center_widget)  # Layout for center alignment
        center_layout.setContentsMargins(0, 0, 0, 0)  # Set layout margins to 0

        # Guide image
        self.label = QLabel(self)
        self.image = QPixmap(':image/Step2.jpg')
        self.label.setPixmap(self.image)
        self.label.setAlignment(Qt.AlignCenter)

        # Button to go back to ImageMain screen
        self.button1 = QPushButton("이전", self)
        self.button1.setStyleSheet('background-color: #B50039; border: none; color: white; font-size:15px')
        self.button1.clicked.connect(lambda: main_window.load_screen_from_path('screen/calibration/step/step1.py', 'GuideScreen'))

        self.button2 = QPushButton("다음", self)
        self.button2.setStyleSheet('background-color: #B50039; border: none; color: white; font-size:15px')
        self.button2.clicked.connect(lambda: main_window.load_screen_from_path('screen/calibration/step/step3.py', 'GuideScreen3'))

        self.button1.setFixedSize(QSize(180, 48))  # Set fixed size for the button
        self.button2.setFixedSize(QSize(180, 48))  # Set fixed size for the button

        button_layout = QHBoxLayout()  # Create a horizontal layout for the buttons
        button_layout.addWidget(self.button1)  # Add the previous button
        button_layout.addWidget(self.button2)  # Add the next button
        button_layout.setAlignment(Qt.AlignCenter)  # Align the layout to the center
        button_layout.setSpacing(30)  # Set layout margins to 0

        center_layout.addWidget(self.label, alignment=Qt.AlignCenter)  # Add image label to the center layout
        center_layout.addLayout(button_layout)  # Add the button layout to the center layout

        main_layout.addStretch(1)  # Add stretchable space
        main_layout.addWidget(center_widget)  # Add center widget to the main layout
        main_layout.addStretch(1)  # Add stretchable space
