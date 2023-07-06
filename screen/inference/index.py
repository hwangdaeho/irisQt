from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QWidget, QMessageBox, QComboBox, QPushButton, QListWidget, QDialog, QScrollArea, QGridLayout, QSpacerItem, QStackedWidget, QSizePolicy, QCheckBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QMutex, QTimer, QUrl
from PyQt5.QtWidgets import QFileDialog
from PIL.ImageQt import ImageQt
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


class InferenceMain(QWidget):
    def __init__(self, parent=None, stacked_widget=None, main_window=None):
        super().__init__(parent)
        self.initUI()

        # Initialize the state
        self.IsModel = False
        self.folder_created = False
        self.camera_connected = False
        self.config_file = '/home/ubuntu/projects/mmopen/mmdetection/configs/faster_rcnn/faster-rcnn_r50_fpn_1x_coco.py'
        self.checkpoint_file = None
        self.model = None
        self.model_classes = None
        self.visualizer = None
        self.model_label = QLabel(self)  # Added QLabel to display model file name
        self.update_button_states()

        self.thread = VideoThread(self)  # Pass the inference_main instance to the VideoThread constructor
        self.thread.changePixmap.connect(self.setImage)
        self.thread.changePixmapRaw.connect(self.setImageRaw)
        self.thread.start()
    def initUI(self):
        # Define a main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addSpacing(50)

        image_layout = QHBoxLayout()
        # main_layout.addStretch()
        # This is where the original image will go
        self.image_label_raw = QLabel()
        self.image_label_raw.setAlignment(Qt.AlignCenter)  # Align the image to the center
        image_layout.addWidget(self.image_label_raw)  # Add it to the main layout


        # This is where the processed image will go
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)  # Align the image to the center
        image_layout.addWidget(self.image_label)  # Add it to the main layout

        self.show_placeholder_image()
        self.show_placeholder_image_raw()
        combo_layout = QHBoxLayout()
        combo_layout.addSpacing(50)
        combo_layout.setAlignment(Qt.AlignRight)  # Align the image to the center
        combo_layout.setContentsMargins(10, 10, 10, 10)
        # 콤보 박스
        self.algo1 = QComboBox()

        self.algo1.setFixedSize(150, 30)
        self.algo1.setContentsMargins(10, 10, 10, 10)
        combo_layout.addWidget(self.algo1)
        # self.set_algo_type()
        button_layout = QHBoxLayout()

        button_layout.setSpacing(0)  # Set the space between the buttons
        button_layout.setAlignment(Qt.AlignCenter)  # Align the image to the center
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_names = ["모델 등록","카메라 연결", "이미지 저장", "데이터 확인"]
        self.enabled_icons = [ ":image/folder-add.svg",":image/camera.svg", ":image/gallery.svg",  ":image/video-octagon.svg"]
        self.disabled_icons = [ ":image/folder-add.svg",":image/camera2.svg", ":image/gallery.svg",  ":image/video-octagon2.svg"]
        # Create the buttons and add them to the layout
        self.buttons = []
        for i, name in enumerate(button_names):
            button = QToolButton()
            button.setText(name)
            button.setStyleSheet('background-color: #2F2F2F; color: white; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the background to black and text to white
            button.setIcon(QIcon(self.enabled_icons[i]))  # Set the icon
            button.setIconSize(QSize(24, 24))  # Set the icon size
            button.setFixedSize(QSize(126, 100))  # Set the button size
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.buttons.append(button)
            button_layout.addWidget(button)


        # self.buttons[0].clicked.connect(self.load_cfg)  # configFile 불러오기
        self.buttons[0].clicked.connect(self.load_model)  # 모델 불러오기
        self.buttons[1].clicked.connect(self.connect_camera)  # '카메라 연결' 버튼을 connect_camera 함수에 연결
        self.buttons[2].clicked.connect(self.load_image)
        # self.buttons[3].clicked.connect(self.start_recording)  # '영상 저장' 버튼을 start_recording 함수에 연결
        # self.buttons[3].clicked.connect(self.handle_record_button_click)  # '영상 저장' 버튼 클릭 이벤트를 새로운 메소드에 연결합니다.



        # Add the button layout to the main layout
        main_layout.addLayout(image_layout)
        main_layout.addLayout(combo_layout)
        main_layout.addLayout(button_layout)
        main_layout.setSpacing(0)  # Set the space between the image label and the button layout

        # Set the main layout
        self.setLayout(main_layout)

        # Set the background of the widget to black
        self.setStyleSheet('background-color: white;')
        # Connect the '카메라 연결' button to the connect_camera function
        # self.buttons[1].clicked.connect(self.connect_camera)

        # # Create the video thread
        # self.thread = VideoThread()
        # self.thread.changePixmap.connect(self.setImage)
        # # Start the video thread
        # self.thread.start()
    # Add new method to set the ComboBox value
    def set_algo_type(self, algo_type):
        print(algo_type)
        self.algo1.clear()  # Clear all items
        if algo_type == 'Object Detection':
            self.algo1.addItems(['yolov5', 'faster_rcnn'])
            self.algo1.currentIndexChanged.connect(self.change_config_file)
        elif algo_type == 'Classification':
            self.algo1.addItems(['d', 'e', 'f'])
        elif algo_type == 'Segmentation':
            self.algo1.addItems(['g', 'h', 'i'])
        else:
            print(f'Error: Unknown algo_type {algo_type}')
    def change_config_file(self, index):
        item = self.algo1.itemText(index)
        if item == 'yolov5':
            self.config_file = '/home/ubuntu/projects/robot/iris/odCfgFile/faster-rcnn_r50_fpn_1x_coco.py'
        elif item == 'faster_rcnn':
            self.config_file = 'odCfgFile/faster-rcnn_r50_fpn_1x_coco.py'
    # '모델 등록' 버튼이 클릭되었을 때 호출되는 함수
    def show_placeholder_image(self):
        # Load your placeholder image
        print('show_placeholder_image')
        placeholder = QImage(":image/null.png")
        # Display the placeholder image
        self.setImage(placeholder)
    def show_placeholder_image_raw(self):
        # Load your placeholder image
        print('show_placeholder_image_raw')
        placeholder = QImage(":image/null.png")
        # Display the placeholder image
        self.setImageRaw(placeholder)
    def load_model(self):
        from mmdet.apis import init_detector, inference_detector
        from mmdet.registry import VISUALIZERS
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self,"Load Model", "","All Files (*);;Model Files (*.pth)", options=options)
        if fileName:
            print(fileName)
            self.checkpoint_file = fileName  # save model path
            self.model = init_detector(self.config_file, self.checkpoint_file, device='cuda:0')
            self.model_classes = self.model.dataset_meta['classes']
            self.visualizer = VISUALIZERS.build(self.model.cfg.visualizer)
            self.model_label.setText(os.path.basename(fileName))  # Show model file name on QLabel
            self.IsModel = True
        self.update_button_states()

    def load_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self,"Load Image", "","Image Files (*.png *.jpg *.bmp)", options=options)
        if fileName:
            img = cv2.imread(fileName)
            result = inference_detector(self.model, img)  # infer image with the model
            img = self.visualizer.draw_results(img, self.model, result)
            qt_img = self.convert_cv_qt(img)
            self.image_label.setPixmap(qt_img)


    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


    @pyqtSlot(QImage)
    def setImage(self, image):
        self.current_image = image
        self.image_label.setPixmap(QPixmap.fromImage(image))
        self.image_label.setContentsMargins(0, 0, 0, 0)
    @pyqtSlot(QImage)
    def setImageRaw(self, image):
        self.current_image_raw = image
        self.image_label_raw.setPixmap(QPixmap.fromImage(image))
        self.image_label_raw.setContentsMargins(0, 0, 0, 0)
    def connect_camera(self):
        # If the camera is already connected, disconnect it
        if self.thread.is_connected:
            self.thread.disconnect_camera()
            self.buttons[1].setText("카메라 연결")
            self.camera_connected = False
            self.show_placeholder_image()  # Add this line
            self.show_placeholder_image_raw()
        else:

            # Display a dialog with the available cameras
            cameras = rs.context().devices
            camera_names = [camera.get_info(rs.camera_info.name) for camera in cameras]

            if camera_names:
                camera_name, ok = QInputDialog.getItem(self, "Connect to camera", "Choose a camera:", camera_names, 0, False)

                if ok and camera_name:
                    connected = self.thread.connect_camera(camera_name)
                    if connected:
                        self.buttons[1].setText("연결 해제")  # Change the button text
                        self.camera_connected = True
            else:
                QMessageBox.information(self, "No cameras found", "No cameras were found. Please connect a camera and try again.")
                self.show_placeholder_image()  # Add this line
                self.show_placeholder_image_raw()  # Add this line

        self.update_button_states()  # Update button states
    def show_placeholder_image(self):
        # Load your placeholder image
        placeholder = QImage(":image/null.png")
        print('caa')
        # Display the placeholder image
        self.setImage(placeholder)
    def show_placeholder_image_raw(self):
        # Load your placeholder image
        print('aaa')
        placeholder = QImage(":image/null.png")

        # Display the placeholder image
        self.setImageRaw(placeholder)

    def update_button_states(self):
        self.buttons[0].setEnabled(True)  # '모델 업로드' button
        self.buttons[1].setEnabled(self.IsModel)  # '생성' button
        self.buttons[2].setEnabled(self.IsModel)  # '이미지 저장' button
        self.buttons[3].setEnabled(self.IsModel)  # '영상 저장' button

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

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)  # For the processed image
    changePixmapRaw = pyqtSignal(QImage)  # For the raw image

    def __init__(self, inference_main, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inference_main = inference_main
        self.mutex = QMutex()  # Add a mutex
        self.video_writer = None  # Add a video writer

    def run(self):
        from mmdet.apis import inference_detector
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.is_connected = False

        while True:
            self.mutex.lock()  # Lock the mutex
            is_connected = self.is_connected  # Store the flag value in a local variable
            self.mutex.unlock()  # Unlock the mutex

            if is_connected:
                frames = self.pipeline.wait_for_frames()
                color_frame = frames.get_color_frame()

                if not color_frame:
                    continue

                color_image = np.asanyarray(color_frame.get_data())

                rgbImageRaw = np.copy(color_image)
                h, w, ch = rgbImageRaw.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImageRaw.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmapRaw.emit(p)
                # Apply the model and draw bounding boxes
                if self.inference_main.model is not None:
                    result = inference_detector(self.inference_main.model, color_image)
                    combined_result = []

                    pred_instances = result.pred_instances
                    labels = pred_instances.labels.cpu().numpy()
                    bboxes = pred_instances.bboxes.cpu().numpy()
                    scores = pred_instances.scores.cpu().numpy()

                    for label, bbox, score in zip(labels, bboxes, scores):
                        combined_result.append(('model1', self.inference_main.model_classes[label], np.append(bbox, score)))

                    for model_id, label, bbox_and_score in combined_result:
                        bbox = bbox_and_score[:4]
                        score = bbox_and_score[4]
                        if score >= 0.9:
                            x1, y1, x2, y2 = bbox.astype(int)
                            if model_id == 'model1':
                                color = (0, 0, 255)
                            cv2.rectangle(color_image, (x1, y1), (x2, y2), color, 2)
                            text = f"Label: {label}, Score: {score:.2f}"
                            cv2.putText(color_image, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


                rgbImage = color_image
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


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
