from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys

class ImageWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Display')

        # Create a label and load an image
        self.label = QLabel(self)
        self.pixmap = QPixmap('image/logo.png')
        self.label.setPixmap(self.pixmap)

        # Add the label to a QVBoxLayout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageWindow()
    sys.exit(app.exec_())
