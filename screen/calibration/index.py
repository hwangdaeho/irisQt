from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from screen.calibration.step.step1 import CalibrationStep1Widget

class CalibrationMain(QWidget):
    def __init__(self, *args, **kwargs):
        super(CalibrationMain, self).__init__(*args, **kwargs)

        self.stacked_widget = QStackedWidget()
        # self.step1 = CalibrationStep1Widget()

        # Create a new QLabel
        self.label = QLabel("화면이 전환되었습니다. 캘리브레이션", self)
        self.label.setAlignment(Qt.AlignCenter)  # Center alignment
        self.label.setStyleSheet("font-size: 20px; color: blue;")  # Set font size and color

        # self.stacked_widget.addWidget(self.step1)
        self.stacked_widget.addWidget(self.label)

        # Create a layout
        self.layout = QVBoxLayout()

        # Add widgets to the layout
        self.layout.addWidget(self.stacked_widget)
        # self.layout.addWidget(self.label)

        # Set the layout to the CalibrationMain
        self.setLayout(self.layout)
