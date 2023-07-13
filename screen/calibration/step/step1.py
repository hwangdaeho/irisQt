from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

class GuideScreen(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel('This is Calibration Step 1')
        layout.addWidget(label)
        self.setLayout(layout)
