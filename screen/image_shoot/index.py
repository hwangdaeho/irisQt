from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QWidget, QMessageBox, QPushButton, QListWidget, QDialog, QScrollArea, QGridLayout, QSpacerItem, QStackedWidget, QSizePolicy, QCheckBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QMutex, QTimer, QUrl
from PyQt5.QtWidgets import QFileDialog
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QMainWindow
import cv2
import pyrealsense2 as rs
import numpy as np
import os
import datetime
from toast import Toast
import glob
from functools import partial
class ImageMain(QWidget):
    def __init__(self, parent=None, stacked_widget=None, main_window=None):
        super().__init__(parent)
        self.initUI()

         # Initialize the state
        self.camera_connected = False
        self.folder_created = False
        self.is_recording = False  # 추가

        self.update_button_states()

    def initUI(self):
        # Define a main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addSpacing(50)
        # main_layout.addStretch()
        # This is where the image will go
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)  # Align the image to the center
        # main_layout.addStretch()
        main_layout.addWidget(self.image_label)

        self.show_placeholder_image()
        # 영상 녹화
        self.recording_start_time = None
        self.recording_timer = QTimer()
        self.recording_time = 0  # 추가: 녹화 시간을 저장할 변수
        self.recording_timer.timeout.connect(self.update_recording_time)


        # Define a horizontal layout for the buttons

        button_layout = QHBoxLayout()

        button_layout.setSpacing(0)  # Set the space between the buttons
        button_layout.setAlignment(Qt.AlignCenter)  # Align the image to the center
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_names = ["카메라 연결", "경로설정", "이미지 저장", "영상 저장",  "데이터 보기"]
        self.enabled_icons = [":image/camera.svg", ":image/folder-add.svg", ":image/gallery.svg", ":image/video.svg", ":image/video-octagon.svg"]
        self.disabled_icons = [":image/camera2.svg", ":image/folder-add2.svg", ":image/gallery2.svg", ":image/video2.svg", ":image/video-octagon2.svg"]
        # Create the buttons and add them to the layout
        self.buttons = []
        for i, name in enumerate(button_names):
            button = QToolButton()
            button.setText(name)
            button.setStyleSheet('background-color: #2F2F2F; color: white; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the background to black and text to white
            button.setCursor(Qt.PointingHandCursor)
            button.setIcon(QIcon(self.enabled_icons[i]))  # Set the icon
            button.setIconSize(QSize(24, 24))  # Set the icon size
            button.setFixedSize(QSize(128, 100))  # Set the button size
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.buttons.append(button)
            button_layout.addWidget(button)


        self.buttons[0].clicked.connect(self.connect_camera)  # '카메라 연결' 버튼을 connect_camera 함수에 연결
        self.buttons[1].clicked.connect(self.create_folder)  # '생성' 버튼을 create_folder 함수에 연결
        self.buttons[2].clicked.connect(self.save_image)
        # self.buttons[3].clicked.connect(self.start_recording)  # '영상 저장' 버튼을 start_recording 함수에 연결
        self.buttons[3].clicked.connect(self.handle_record_button_click)  # '영상 저장' 버튼 클릭 이벤트를 새로운 메소드에 연결합니다.
        self.buttons[4].clicked.connect(self.show_file_list)  # '완료' 버튼을 stop_recording 함수에 연결



        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)
        main_layout.setSpacing(0)  # Set the space between the image label and the button layout

        # Set the main layout
        self.setLayout(main_layout)

        # Set the background of the widget to black
        self.setStyleSheet('background-color: white;')
        # Connect the '카메라 연결' button to the connect_camera function
        # self.buttons[1].clicked.connect(self.connect_camera)

        # Create the video thread
        self.thread = VideoThread()
        self.thread.changePixmap.connect(self.setImage)

        # Start the video thread
        self.thread.start()
    def guide_button_click(self):
        # 'capture_guide.png'는 촬영 가이드 이미지 파일의 경로입니다.
        self.guide_window = GuideWindow(':image/ImageGuide.png')
        self.guide_window.show()
    def handle_record_button_click(self):
        if self.thread.get_is_recording():  # 녹화가 이미 진행 중이라면
            print('stop')
            self.stop_recording()  # 녹화를 중지합니다.
        else:  # 녹화가 진행 중이 아니라면
            print('start')
            self.start_recording()  # 녹화를 시작합니다.
    def start_recording(self):
        if hasattr(self, 'folder_path') and self.camera_connected:  # Only allow to start recording when the camera is connected and a folder is created
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            video_path = os.path.join(self.folder_path, f"{timestamp}.mp4")
            self.thread.start_recording(video_path)
            self.recording_start_time = datetime.datetime.now()
            self.recording_timer.start(1000)  # Update every second
        else:
            QMessageBox.information(self, "No camera or folder", "Please connect a camera and create a folder first.")
    def update_recording_time(self):
        if self.recording_start_time is not None:
            self.recording_time += 1  # 녹화 시간 증가
            minutes, seconds = divmod( self.recording_time, 60)
            hours, minutes = divmod(minutes, 60)
            self.buttons[3].setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    def stop_recording(self):
        if self.camera_connected:  # Only allow to stop recording when the camera is connected
            self.thread.stop_recording()
            self.recording_timer.stop()
            self.recording_start_time = None
            self.buttons[3].setText("녹화 시작")
            self.recording_time = 0  # 녹화 시간을 0으로 재설정
        else:
            QMessageBox.information(self, "No camera", "Please connect a camera first.")

    def create_folder(self):
        if self.camera_connected:  # Only allow to create a folder when the camera is connected
            folder_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
            if folder_path:
                self.folder_path = folder_path
                self.folder_created = True
                self.update_button_states()  # Update button states
    def update_button_states(self):
        self.buttons[0].setEnabled(True)  # '카메라 연결' button
        self.buttons[1].setEnabled(self.camera_connected)  # '생성' button
        self.buttons[2].setEnabled(self.camera_connected and self.folder_created)  # '이미지 저장' button
        self.buttons[3].setEnabled(self.camera_connected and self.folder_created)  # '영상 저장' button

        # Update button colors
        for i, button in enumerate(self.buttons):
            if button.isEnabled():
                button.setEnabled(True)
                button.setIcon(QIcon(self.enabled_icons[i]))  # Change this line
                button.setStyleSheet('background-color: #2F2F2F; color: white; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the enabled button color
            else:
                button.setEnabled(False)
                button.setIcon(QIcon(self.disabled_icons[i]))  # Change this line
                button.setStyleSheet('background-color: #2F2F2F; color: #525252; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the disabled button color
    def save_image(self):
        if hasattr(self, 'folder_path'):
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            image_path = os.path.join(self.folder_path, f"{timestamp}.jpg")
            # save the image
            self.current_image.save(image_path, "JPEG")
            self.toast = Toast(self, "이미지 촬영이 완료되었습니다.") # Make toast a class attribute
            self.toast.show()
        else:
            QMessageBox.information(self, "No folder selected", "Please create a folder first.")
    def show_file_list(self):
        if hasattr(self, 'folder_path'):
            self.file_list_window = FileDisplayWidget(self.folder_path)
            self.file_list_window.show()
        else:
            QMessageBox.information(self, "No folder selected", "Please create a folder first.")


    @pyqtSlot(QImage)
    def setImage(self, image):
        self.current_image = image
        self.image_label.setPixmap(QPixmap.fromImage(image))
        self.image_label.setContentsMargins(0, 0, 0, 0)

    def connect_camera(self):
        # If the camera is already connected, disconnect it
        if self.thread.is_connected:
            self.thread.disconnect_camera()
            self.buttons[0].setText("카메라 연결")
            self.camera_connected = False
            self.show_placeholder_image()  # Add this line
        else:
            # Display a dialog with the available cameras
            cameras = rs.context().devices
            camera_names = [camera.get_info(rs.camera_info.name) for camera in cameras]

            if camera_names:
                camera_name, ok = QInputDialog.getItem(self, "Connect to camera", "Choose a camera:", camera_names, 0, False)

                if ok and camera_name:
                    connected = self.thread.connect_camera(camera_name)
                    if connected:
                        self.buttons[0].setText("연결 해제")  # Change the button text
                        self.camera_connected = True
            else:
                QMessageBox.information(self, "No cameras found", "No cameras were found. Please connect a camera and try again.")
                self.show_placeholder_image()  # Add this line

        self.update_button_states()  # Update button states
    def show_placeholder_image(self):
        # Load your placeholder image
        placeholder = QImage(":image/null.png")

        # Display the placeholder image
        self.setImage(placeholder)

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mutex = QMutex()  # Add a mutex
        self.is_recording = False  # Add a flag for recording
        self.video_writer = None  # Add a video writer

    def run(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.is_connected = False

        while True:
            self.mutex.lock()  # Lock the mutex
            is_connected = self.is_connected  # Store the flag value in a local variable
            is_recording = self.is_recording  # Store the flag value in a local variable
            self.mutex.unlock()  # Unlock the mutex

            if is_connected:
                frames = self.pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()

                if not color_frame:
                    continue

                color_image = np.asanyarray(color_frame.get_data())
                rgbImage = color_image
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

                if is_recording and self.video_writer is not None:
                    bgr_frame = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2BGR)
                    # If we are recording, write the frame into the video writer
                    self.video_writer.write(bgr_frame)
    def get_is_recording(self):
        self.mutex.lock()  # Lock the mutex
        is_recording = self.is_recording
        self.mutex.unlock()  # Unlock the mutex
        return is_recording
    def connect_camera(self, camera_name):
        self.mutex.lock()  # Lock the mutex
        try:
            self.pipeline.start(self.config)
            self.is_connected = True
            return True  # Add this line
        except RuntimeError as e:
            QMessageBox.information(self, "Connection failed", "Could not connect to the selected camera: {}".format(e))
        finally:
            self.mutex.unlock()  # Unlock the mutex in a finally block to ensure it gets unlocked

    def disconnect_camera(self):
        self.mutex.lock()  # Lock the mutex
        if self.is_connected:
            self.pipeline.stop()
            self.is_connected = False  # Set this flag to False after stopping the pipeline
        self.mutex.unlock()  # Unlock the mutex
    def start_recording(self, video_path):
        self.mutex.lock()  # Lock the mutex
        if self.is_connected:
            # Create a video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))
            self.is_recording = True  # Set this flag to True when starting recording
            print('start')
        self.mutex.unlock()  # Unlock the mutex

    def stop_recording(self):
        self.mutex.lock()  # Lock the mutex
        if self.is_recording:
            self.is_recording = False  # Set this flag to False when stopping recording
            # Release the video writer
            self.video_writer.release()
            self.video_writer = None
            print('stop')
        self.mutex.unlock()  # Unlock the mutex




class ImageViewer(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        print(self.image_path)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel()

        pixmap = QPixmap(self.image_path)
        self.label.setPixmap(pixmap)
        self.layout.addWidget(self.label)

        # self.back_button = QPushButton("Back")
        # self.back_button.clicked.connect(self.back)
        # self.layout.addWidget(self.back_button)

    def back(self):
        self.close()  # 현재 창을 닫음

class FileDisplayWidget(QWidget):
    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.image_viewer = None
        self.checkboxes = []  # 체크박스 목록
        self.to_delete = []  # 삭제할 파일 목록
        self.image_button = None  # 이미지 버튼
        self.video_button = None  # 비디오 버튼
        self.video_player = None  # 비디오 플레이어
        self.delete_button = None  # 선택 삭제 버튼
        self.initUI()
        self.setStyleSheet("""
            QScrollArea { border: none;}
        """)

    def initUI(self):
        self.image_button = QPushButton("이미지")
        self.image_button.setFixedSize(100, 50)
        self.image_button.setStyleSheet("QPushButton { background-color: #B50039; border:none; color:#ffffff; }")
        self.image_button.clicked.connect(self.show_images)

        self.video_button = QPushButton("비디오")
        self.video_button.setFixedSize(100, 50)
        self.video_button.setStyleSheet("QPushButton { background-color: #ffffff; border:none;  }")
        self.video_button.clicked.connect(self.show_videos)

        self.line_widget = QWidget()  # 선을 그릴 위젯
        self.line_widget.setFixedHeight(3)  # 선의 높이 설정
        self.line_widget.setStyleSheet("background-color: #B50039;")  # 선의 색상 설정

        self.image_widgets = []  # ImageWidget 참조를 저장할 리스트
        self.all_select_check = QCheckBox("전체 선택")
        self.all_select_check.stateChanged.connect(self.handle_all_select_check)
        self.delete_button = QPushButton("선택 삭제")
        self.delete_button.setFixedSize(100, 50)
        self.delete_button.setStyleSheet("QPushButton { background-color: #393939; border:none; color:#ffffff;}")
        self.delete_button.clicked.connect(self.select_delete)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content_widget)
        self.scroll_area.setWidget(self.scroll_content_widget)

        self.load_files()

        main_layout = QVBoxLayout(self)

        button_layout_top = QHBoxLayout()
        button_layout_top.addWidget(self.image_button)
        button_layout_top.addWidget(self.video_button)
        button_layout_top.setAlignment(Qt.AlignLeft)

        button_layout_bottom = QHBoxLayout()
        button_layout_bottom.addWidget(self.all_select_check)  # 체크박스 추가
        button_layout_bottom.addWidget(self.delete_button)
        button_layout_bottom.setSpacing(20)
        button_layout_bottom.setContentsMargins(10, 10, 10, 10)
        button_layout_bottom.setAlignment(Qt.AlignRight)

        main_layout.addLayout(button_layout_top)
        main_layout.addWidget(self.line_widget)  # 선 위젯 추가
        main_layout.addLayout(button_layout_bottom)
        main_layout.addWidget(self.scroll_area)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(50, 50, 50, 50)
        self.resize(1200, 800)

    def handle_all_select_check(self, state):
        for image_widget in self.image_widgets:
            image_widget.checkbox.setChecked(state == Qt.Checked)

    def load_files(self):
        self.image_widgets.clear()
        row = 0
        column = 0

        files = []

        if self.video_button.styleSheet() == "QPushButton { background-color: #B50039; border:none; color:#ffffff;}":  # 비디오 버튼이 선택된 경우
            for ext in ['*.mp4']:
                files.extend(glob.glob(os.path.join(self.folder_path, ext)))
        else:
            for ext in ['*.jpg', '*.png']:
                files.extend(glob.glob(os.path.join(self.folder_path, ext)))


        files.sort()  # 파일을 정렬합니다.

        for file in files:
            image_widget = ImageWidget(file, self)  # ImageWidget 생성
            self.image_widgets.append(image_widget)  # 리스트에 ImageWidget을 추가합니다.
            self.scroll_layout.addWidget(image_widget, row, column, alignment=Qt.AlignTop)  # 중앙에 위젯을 배치

            column += 1
            if column == 4:
                column = 0
                row += 1

        self.scroll_layout.update()


    def handle_checkbox(self, state, file):
        if state == Qt.Checked:
            self.to_delete.append(file)
        else:
            self.to_delete.remove(file)

    def select_delete(self):
        to_delete = []  # 삭제할 위젯의 목록

        # 삭제할 위젯 찾기
        for i in reversed(range(self.scroll_layout.count())):
            image_widget = self.scroll_layout.itemAt(i).widget()
            if isinstance(image_widget, ImageWidget) and image_widget.checkbox.isChecked():
                to_delete.append(image_widget)

        # 레이아웃에서 위젯 제거
        for image_widget in to_delete:
            image_widget.hide()
            image_widget.deleteLater()
            self.scroll_layout.removeWidget(image_widget)

        # 파일 삭제
        for image_widget in to_delete:
            os.remove(image_widget.file_path)

        # 이미지 위젯 제거
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()

        self.load_files()  # 파일 목록을 새로고침

    def show_images(self):
        self.image_button.setStyleSheet("QPushButton { background-color: #B50039; border:none; color:#ffffff;}")  # 이미지 버튼을 빨간색으로 설정
        self.video_button.setStyleSheet("QPushButton { background-color: white; border:none;}")  # 비디오 버튼 스타일 초기화

        # 이미지 위젯 제거
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()

        row = 0
        column = 0

        image_files = []
        for ext in ['*.jpg', '*.png']:
            image_files.extend(glob.glob(os.path.join(self.folder_path, ext)))

        image_files.sort()  # 이미지 파일을 정렬합니다.

        for file in image_files:
            image_widget = ImageWidget(file, self)  # ImageWidget 생성
            self.image_widgets.append(image_widget)  # 리스트에 ImageWidget을 추가합니다.
            self.scroll_layout.addWidget(image_widget, row, column, alignment=Qt.AlignTop)  # 중앙에 위젯을 배치

            column += 1
            if column == 4:
                column = 0
                row += 1

        self.scroll_layout.update()


    def show_videos(self):
        self.image_button.setStyleSheet("QPushButton { background-color: white; border:none; }")  # 이미지 버튼을 빨간색으로 설정
        self.video_button.setStyleSheet("QPushButton { background-color: #B50039; border:none; color:#ffffff;}")    # 비디오 버튼 스타일 초기화

        # 이미지 위젯 제거
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()
        row = 0
        column = 0

        for ext in ['*.mp4']:
            for file in glob.glob(os.path.join(self.folder_path, ext)):
                if ext == '*.mp4':
                    thumbnail = self.extract_video_thumbnail(file)
                    if thumbnail is not None:
                        image_widget = ImageWidget(file, self)  # ImageWidget 생성
                        self.scroll_layout.addWidget(image_widget, row, column, alignment=Qt.AlignTop)  # 중앙에 위젯을 배치
                        self.image_widgets.append(image_widget)  # 리스트에 ImageWidget을 추가합니다.
                column += 1
                if column == 4:
                    column = 0
                    row += 1

        self.scroll_layout.update()

    def extract_video_thumbnail(self, file):
        cap = cv2.VideoCapture(file)

        # Read the first frame of the video
        ret, frame = cap.read()

        if ret:
            # Convert the frame to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create a QImage from the frame
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qimage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)

            # Create a QPixmap from the QImage
            pixmap = QPixmap.fromImage(qimage)

            return pixmap
        else:
            return QPixmap()  # Return an empty QPixmap if the function fails



class ImageWidget(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

        main_layout = QVBoxLayout(self)

        checkbox_layout = QHBoxLayout()
        self.checkbox = QCheckBox(self)
        self.checkbox.stateChanged.connect(self.handle_checkbox)
        checkbox_layout.addWidget(self.checkbox, alignment=Qt.AlignRight)
        main_layout.addLayout(checkbox_layout)

        image_label = QLabel(self)
        try:
            if self.file_path.endswith(".mp4"):
                cap = cv2.VideoCapture(self.file_path)

                # Read the first frame of the video
                ret, frame = cap.read()

                if ret:
                    # Convert the frame to RGB format
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Create a QImage from the frame
                    height, width, channel = frame.shape
                    bytesPerLine = 3 * width
                    qimage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)

                    # Create a QPixmap from the QImage
                    pixmap = QPixmap.fromImage(qimage)
                else:
                    raise ValueError("Failed to read video file")
            else:
                pixmap = QPixmap(self.file_path)
                if pixmap.isNull():
                    raise ValueError("The QPixmap is null")

            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Failed to create QPixmap from file {self.file_path}: {e}")

        image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(image_label)

        main_layout.setContentsMargins(0, 0, 0, 0)

    def handle_checkbox(self, state):
        parent = self.parent()
        while parent is not None and not isinstance(parent, FileDisplayWidget):
            parent = parent.parent()

        if parent is not None:
            if state == Qt.Checked:
                parent.handle_checkbox(Qt.Checked, self.file_path)
            else:
                parent.handle_checkbox(Qt.Unchecked, self.file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_large_image()

    def show_large_image(self):
        print("show_large_image is called with file:", self.file_path)
        self.image_viewer = ImageViewer(self.file_path)
        self.image_viewer.show()



class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, file, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.file = file

    def mousePressEvent(self, event):
        self.clicked.emit()

class VideoPlayer(QWidget):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Player")
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        btns_layout = QVBoxLayout()
        btns_layout.addWidget(videoWidget)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))

        self.play_button = QPushButton()
        self.play_button.setEnabled(True)
        self.play_button.setText('Play')
        self.play_button.clicked.connect(self.play_video)

        btns_layout.addWidget(self.play_button)
        self.setLayout(btns_layout)

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()