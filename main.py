from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QDesktopWidget, QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from side_menu import create_side_menu
from screen.image_shoot.index import ImageMain
from screen.calibration.index import CalibrationMain
from screen.inference.index import InferenceMain
import sys
import importlib.util
from PyQt5.QtWidgets import QWidget
import resources
import os
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("이미지 촬영")
        self.setWindowIcon(QIcon(":/image/logo.png"))
        self.inference_main = InferenceMain()  # Add this line
        self.initUI()

    def initUI(self):
        self.resize_screen(80)
        self.center()

        self.stacked_widget = QStackedWidget()
        self.ImageMain = ImageMain()
        self.CalibrationMain = CalibrationMain()
        self.stacked_widget.addWidget(self.ImageMain)  # ImageMain is added first
        self.stacked_widget.addWidget(self.CalibrationMain)
        self.header_label = QLabel("이미지 촬영")
        self.header_label.setStyleSheet("color: #FFFFFF; font-size: 18px; margin-left: 10px;")


        # Create a logo label
        logo_label = QLabel()
        logo_image = QPixmap(":image/logo.svg")
        logo_label.setPixmap(logo_image)
        logo_label.setStyleSheet("margin-left:16px;")

        # Create a big header
        big_header_label = QLabel("Big Header")
        big_header_label.setStyleSheet("background-color: white; color: white;")  # blue color for header

        big_header = QWidget()
        big_header.setFixedHeight(60)
        big_header_layout = QHBoxLayout()
        big_header_layout.addWidget(logo_label)
        big_header_layout.addWidget(big_header_label)
        big_header.setLayout(big_header_layout)

        # Create a header widget
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #B50039;")  # blue color for header
        header_widget.setContentsMargins(0, 0, 0, 0)  # Remove margins
        header_layout = QHBoxLayout()
        header_label = QLabel("IRIS")
        # header_label.setStyleSheet("color: white; font-size: 40px;")
        header_layout.addWidget(self.header_label)

        # Create guide button
        self.guide_button = QPushButton("가이드 보기")
        self.guide_button.hide()  # 초기에는 가이드 버튼을 숨겨둡니다.
        self.guide_button.setFixedSize(100, 40)
        self.guide_button.setStyleSheet("background-color: white; color: #B50039; font-weight: bold;")
        self.update_header("이미지 학습 촬영", "screen/image_shoot/step/step1.py", "GuideScreen")

        header_layout.addWidget(self.guide_button)
        header_widget.setLayout(header_layout)
        header_widget.setFixedHeight(70)
        side_menu = create_side_menu(self.stacked_widget, self)
        side_menu.setStyleSheet("background-color: #F7F7F7;")  # green color for side menu
        side_menu.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Create right layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(header_widget)
        right_layout.addWidget(self.stacked_widget)
        right_layout.setSpacing(0)  # Remove space between widgets

        # Create middle layout
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(side_menu, 1)
        middle_layout.addLayout(right_layout, 9)
        middle_layout.setContentsMargins(0, 0, 0, 0)  # 컨텐츠의 여백을 없앱니다.
        middle_layout.setSpacing(0)  # Remove space between widgets

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(big_header)
        main_layout.addLayout(middle_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 컨텐츠의 여백을 없앱니다.
        main_layout.setSpacing(0)  # Remove space between widgets

        # Create a widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setStyleSheet("background-color: white;")  # yellow color for main widget
        central_widget.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.setCentralWidget(central_widget)
        self.show()


    def resize_screen(self, percentage):
        screen = QDesktopWidget().screenGeometry()
        self.resize(int(screen.width() * percentage / 100), int(screen.height() * percentage / 100))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_header(self, text, guide_path=None, guide_class=None):
        self.header_label.setText(text)
        if text == "실시간 모니터링 & 운영":
            self.guide_button.hide()
        else:
            if guide_path and guide_class:
                self.guide_button.show()  # 가이드 버튼이 있으면 표시
                self.guide_button.clicked.connect(lambda: self.load_screen_from_path(guide_path, guide_class))
            else:
                self.guide_button.hide()  # 가이드 버튼이 없으면 숨김



    def update_header_text(self, text):
        self.header_label.setText(text)

    def load_screen_from_path(self, path, class_name):
        if class_name == 'InferenceMain':
            self.stacked_widget.addWidget(self.inference_main)
            self.stacked_widget.setCurrentIndex(self.stacked_widget.count() - 1)
        else:
            screen_instance = self.load_screen(path, class_name)
            self.stacked_widget.addWidget(screen_instance)
            self.stacked_widget.setCurrentIndex(self.stacked_widget.count() - 1)

    def set_algo_type(self, algo_type):
        # Create the InferenceMain instance here, only if it's not already created
        if self.inference_main is None:
            self.inference_main = InferenceMain()
            # Then you can add the instance to your stack, set it as the central widget, or whatever your design requires

        # Now you can call set_algo_type on the InferenceMain instance
        self.inference_main.set_algo_type(algo_type)
    def load_screen(self, path, class_name):
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(__file__)

        path = os.path.join(base_dir, path)

        spec = importlib.util.spec_from_file_location(class_name, path)
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)
        screen_class = getattr(module, class_name)

        return screen_class(self.stacked_widget, self)  # pass the required arguments



        return screen_class()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
