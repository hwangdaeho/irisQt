from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

class CalibrationStep1Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super(CalibrationStep1Widget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        label = QLabel('This is Calibration Step 1')
        layout.addWidget(label)
        self.setLayout(layout)
