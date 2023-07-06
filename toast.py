from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor
class Toast(QLabel):
    def __init__(self, parent=None, message=""):
        QLabel.__init__(self, parent)
        self.setFixedSize(150, 100)
        self.setStyleSheet("""
            background-color: rgba(38,38,38,90%);
            color: white;
            border-radius: 10px;
            font: 15px '나눔스퀘어';
            padding: 15px;
            text-align: center;
            """)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText(message)

        # 추가된 부분: 메시지 위치 조정
        self.move(parent.width()/2 - self.width()/2, parent.height()/2 - self.height()/2)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.hide)
        self.timer.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.setOpacity(0.5)
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)

    def showEvent(self, QShowEvent):
        QTimer.singleShot(3000, self.close)

def toast(parent, message, duration=2000):
    t = Toast(parent, message, duration)
    t.show()
