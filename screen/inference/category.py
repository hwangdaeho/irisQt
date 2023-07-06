from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QToolButton
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QSize, QPoint, QRectF

class ShadowButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        # 그림자 효과에 사용할 속성 설정
        self.shadow_color = QColor(0, 0, 0, 100)
        self.shadow_radius = 10
        self.shadow_offset = QPoint(0, 0)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.underMouse():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            path = QPainterPath()
            path.addRoundedRect(
                QRectF(self.rect().translated(self.shadow_offset)), self.shadow_radius, self.shadow_radius
            )

            painter.setBrush(QBrush(self.shadow_color))
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

class Category(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)

        self.main_window = main_window

        button_size = QSize(420, 482)
        layout = QHBoxLayout(self)

        button1 = ShadowButton(self)
        button1.setIcon(QIcon(QPixmap(":image/ObjectDetection.png")))
        button1.setStyleSheet("border:none;")
        button1.setIconSize(button_size)
        button1.clicked.connect(lambda: self.load_screen('InferenceMain', 'Object Detection'))  # Add event handler
        layout.addWidget(button1)

        button2 = ShadowButton(self)
        button2.setIcon(QIcon(QPixmap(':image/Classification.png')))
        button2.setStyleSheet("border:none;")
        button2.setIconSize(button_size)
        button2.clicked.connect(lambda: self.load_screen('InferenceMain', 'Classification'))  # Add event handler
        layout.addWidget(button2)

        button3 = ShadowButton(self)
        button3.setIcon(QIcon(QPixmap(':image/Segmentation.png')))
        button3.setStyleSheet("border:none;")
        button3.setIconSize(button_size)
        button3.clicked.connect(lambda: self.load_screen('InferenceMain', 'Segmentation'))  # Add event handler
        layout.addWidget(button3)

    def load_screen(self, screen_name, algo_type):
        self.main_window.load_screen_from_path('screen/inference/index.py', screen_name)
        # Assuming that you have a method to set the ComboBox value in the InferenceMain class
        self.main_window.set_algo_type(algo_type)
