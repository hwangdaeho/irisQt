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
from threading import Lock
import cv2
import pyrealsense2 as rs
import numpy as np
import os
import datetime
from toast import Toast
import glob
from functools import partial
import random
from PIL import Image
from mmdet.apis import init_detector
from mmseg.apis import init_model
from mmdet.registry import VISUALIZERS as mmdet_VISUALIZERS
from mmyolo.registry import VISUALIZERS as mmyolo_VISUALIZERS
from mmdet.apis import inference_detector
from mmseg.apis import inference_model
class InferenceMain(QWidget):
    def __init__(self, parent=None, stacked_widget=None, main_window=None):
        super().__init__(parent)
        self.initUI()

        # Initialize the state
        self.IsModel = False
        self.folder_created = False
        self.camera_connected = False
        self.config_file = None
        self.checkpoint_file = None
        self.model = None
        self.model_classes = None
        self.num_classes = None
        self.visualizer = None
        self.isYolo = None
        self.update_button_states()

        self.thread = VideoThread(self)  # Pass the inference_main instance to the VideoThread constructor
        self.thread.changePixmap.connect(self.setImage)
        self.thread.changePixmapRaw.connect(self.setImageRaw)
        self.thread.start()
        self.current_algo_type = None
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

        self.model_label = QLabel()  # Added QLabel to display model file name
        label_layout = QVBoxLayout()
        label_layout.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(self.model_label)
        combo_layout.addLayout(label_layout)
        self.algo1.setFixedSize(150, 30)
        self.algo1.setContentsMargins(10, 10, 10, 10)
        combo_layout.addWidget(self.model_label)
        combo_layout.addWidget(self.algo1)
        # self.set_algo_type()
        button_layout = QHBoxLayout()

        button_layout.setSpacing(0)  # Set the space between the buttons
        button_layout.setAlignment(Qt.AlignCenter)  # Align the image to the center
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_names = ["모델 등록","카메라 연결", "이미지 불러오기",]
        self.enabled_icons = [ ":image/folder-add.svg",":image/camera.svg", ":image/gallery.svg"]
        self.disabled_icons = [ ":image/folder-add2.svg",":image/camera2.svg", ":image/gallery2.svg"]
        # Create the buttons and add them to the layout
        self.buttons = []
        for i, name in enumerate(button_names):
            button = QToolButton()
            button.setText(name)
            button.setStyleSheet('background-color: #2F2F2F; color: white; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the background to black and text to white
            button.setIcon(QIcon(self.enabled_icons[i]))  # Set the icon
            button.setCursor(Qt.PointingHandCursor)
            button.setIconSize(QSize(24, 24))  # Set the icon size
            button.setFixedSize(QSize(168, 100))  # Set the button size
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.buttons.append(button)
            button_layout.addWidget(button)


        # self.buttons[0].clicked.connect(self.load_cfg)  # configFile 불러오기
        self.buttons[0].clicked.connect(self.handle_load_model_button_click)  # 모델 불러오기
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
    def handle_load_model_button_click(self):
        print('handle_load_model_button_click')
        if self.current_algo_type == 'Object Detection':
            if self.isYolo =="yolov5":
                self.load_mmyolov_model()
            else:
                self.load_detection_model()
        elif self.current_algo_type == 'Segmentation':
            self.load_segmentation_model()
        elif self.current_algo_type == 'Classification':
            self.load_classification_model()  # 이 함수를 필요에 맞게 구현해야 합니다.
        else:
            print(f'Error: Unknown algo_type {self.current_algo_type}')
    def get_selected_algo_type(self):
        return self.algo1.currentText()
    def set_algo_type(self, algo_type):
        self.current_algo_type = algo_type
        self.algo1.clear()  # Clear all items
        if algo_type == 'Object Detection':
            self.algo1.addItems(['선택해주세요','yolov5', 'faster_rcnn'])
            self.algo1.currentIndexChanged.connect(self.change_config_file)
            self.thread.set_algorithm('ObjectDetection')  # Set the algorithm in the VideoThread
        elif algo_type == 'Classification':
            self.algo1.addItems(['선택해주세요','d', 'e', 'f'])
            self.thread.set_algorithm('Classification')  # Set the algorithm in the VideoThread
        elif algo_type == 'Segmentation':
            self.algo1.addItems(['선택해주세요','pspnet'])
            self.algo1.currentIndexChanged.connect(self.change_config_file)
            self.thread.set_algorithm('Segmentation')  # Set the algorithm in the VideoThread
        else:
            print(f'Error: Unknown algo_type {algo_type}')
    def change_config_file(self, index):
        item = self.algo1.itemText(index)
        if item == 'yolov5':
            self.config_file = 'yoloCfgFile/yolov5/yolov5_s-v61_syncbn_8xb16-300e_coco.py'
            self.isYolo = 'yolov5'
        elif item == 'faster_rcnn':
            self.config_file = 'odCfgFile/faster-rcnn_r50_fpn_1x_coco.py'
            self.isYolo = None
        elif item == 'pspnet':
            self.config_file = 'sgCfgFile/pspnet_r50-d8_4xb2-40k_cityscapes-512x1024.py'
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

    def load_detection_model(self):

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Load Model", "","All Files (*);;Model Files (*.pth)", options=options)
        if fileName:
            print(fileName)
            self.checkpoint_file = fileName  # save model path
            # self.model = init_detector(self.config_file, self.checkpoint_file, device='cuda:0')
            self.model = init_detector(self.config_file, self.checkpoint_file, device='cpu')
            self.model_classes = self.model.dataset_meta['classes']
            print('모델')
            print(self.model.dataset_meta['classes'])
            self.visualizer = mmdet_VISUALIZERS.build(self.model.cfg.visualizer)
            self.model_label.setText(os.path.basename(fileName))  # Show model file name on QLabel
            self.IsModel = True
        self.update_button_states()

    # Segmentation 관련
    def load_segmentation_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Load Model", "","All Files (*);;Model Files (*.pth)", options=options)
        if fileName:
            self.checkpoint_file = fileName  # save model path
            self.model = init_model(self.config_file, self.checkpoint_file, device='cuda:0')
            self.num_classes = self.model.decode_head.conv_seg.out_channels
            self.palette = [[0, 0, 0]]  # Set background color to black
            self.palette += [[random.randint(0, 255) for _ in range(3)] for _ in range(self.num_classes - 1)]  # Other classes get random colors
            self.IsModel = True
        self.update_button_states()
    def load_mmyolov_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Load Model", "","All Files (*);;Model Files (*.pth)", options=options)
        if fileName:
            print(fileName)
            self.checkpoint_file = fileName  # save model path
            # self.model = init_detector(self.config_file, self.checkpoint_file, device='cuda:0')
            self.model = init_detector(self.config_file, self.checkpoint_file, device='cpu')
            self.model_classes = self.model.dataset_meta['classes']
            print('모델')
            print(self.model.dataset_meta['classes'])
            self.visualizer = mmyolo_VISUALIZERS.build(self.model.cfg.visualizer)
            self.model_label.setText(os.path.basename(fileName))  # Show model file name on QLabel
            self.IsModel = True
        self.update_button_states()

    def show_result(self, img, result, opacity=0.5):
        img = img.copy()
        seg_img = np.zeros((img.shape[0], img.shape[1], 3))

        # Convert the predicted segmentation map to numpy array
        pred_labels = result.pred_sem_seg.data.cpu().numpy()[0] # Remove batch dimension

        for label, color in enumerate(self.palette[1:], start=1):
            seg_img[pred_labels == label] = color

        seg_img = Image.fromarray(seg_img.astype(np.uint8)).convert('RGB')
        seg_img = np.array(seg_img).astype(img.dtype)
        seg_img = cv2.addWeighted(img, 1 - opacity, seg_img, opacity, 0)
        return seg_img

    # Segmentation 여기까지


    def load_image(self):

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Load Image", "","Image Files (*.png *.jpg *.bmp)", options=options)
        if fileName:
            img = cv2.imread(fileName)
            img_original = img.copy()  # Keep a copy of the original image

            # Convert the original image to QPixmap and display it on the left side
            qt_img_original = self.convert_cv_qt(img_original)
            self.image_label_raw.setPixmap(qt_img_original)
            if self.current_algo_type == 'Object Detection':
                result = inference_detector(self.model, img)
                combined_result = []
                pred_instances = result.pred_instances
                labels = pred_instances.labels.cpu().numpy()
                bboxes = pred_instances.bboxes.cpu().numpy()
                scores = pred_instances.scores.cpu().numpy()

                for label, bbox, score in zip(labels, bboxes, scores):
                    combined_result.append(('model1', self.model_classes[label], np.append(bbox, score)))

                for model_id, label, bbox_and_score in combined_result:
                    bbox = bbox_and_score[:4]
                    score = bbox_and_score[4]
                    if score >= 0.9:
                        x1, y1, x2, y2 = bbox.astype(int)
                        if model_id == 'model1':
                            color = (0, 0, 255)
                        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                        text = f"Label: {label}, Score: {score:.2f}"
                        cv2.putText(img, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                rgbImage = img
                qt_img = self.convert_cv_qt(rgbImage)
                self.image_label.setPixmap(qt_img)

            elif self.current_algo_type == 'Segmentation':
                print('Segmentation 이미지')
                result = inference_model(self.model, img)  # infer image with the model
                seg_image = self.show_result(img, result, opacity=0.5)
                color_image = seg_image
                # Convert the segmentation result to QPixmap and display it on the right side
                qt_img = self.convert_cv_qt(color_image)
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
        # Display the placeholder image
        self.setImage(placeholder)
    def show_placeholder_image_raw(self):
        # Load your placeholder image
        placeholder = QImage(":image/null.png")

        # Display the placeholder image
        self.setImageRaw(placeholder)

    def update_button_states(self):
        self.buttons[0].setEnabled(True)  # '모델 업로드' button
        self.buttons[1].setEnabled(self.IsModel)  # '생성' button
        self.buttons[2].setEnabled(self.IsModel)  # '이미지 저장' button
        # self.buttons[3].setEnabled(self.IsModel)  # '영상 저장' button

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
        self.lock = Lock()
        self.video_writer = None
        self.algorithm = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_capture)
        self.timer.start(1000 / 30)  # Start the timer to call update_frame 30 times per second
        self.is_connected = False  # Initialize the attribute
        self.pipeline = rs.pipeline()
        self.config = rs.config()


    def run_capture(self):
        with self.lock:
            is_connected = self.is_connected

        if is_connected:
            print('run_capture')
            print('is_connected')
            frames = self.pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            print(color_frame)

            if not color_frame:
                return

            color_image = np.asanyarray(color_frame.get_data())

            if self.algorithm == "ObjectDetection":
                print('ObjectDetection')
                self.run_object_detection(color_image)
            elif self.algorithm == "Segmentation":
                self.run_segmentation(color_image)

    def run_object_detection(self, color_image):
        # Apply the model and draw bounding boxes
        if self.inference_main.model:
            result = inference_detector(self.inference_main.model, color_image)
            print('run_object_detection')
            print(result)
            # self.process_result(result, color_image)


    def run_segmentation(self, color_image):

        if self.inference_main.model:
            result = inference_model(self.inference_main.model, color_image)
            # self.process_result(result, color_image)


    def set_algorithm(self, algorithm):
        with self.lock:
            self.algorithm = algorithm

    def run_object_detection(self, color_image):
        #from mmdet.apis import inference_detector
        # Here goes the object detection code
        h, w, ch = color_image.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(color_image.data, w, h, bytesPerLine, QImage.Format_RGB888)
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

        convertToQtFormat = QImage(color_image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.changePixmap.emit(p)



    def run_segmentation(self, color_image):
        #from mmseg.apis import inference_model
        # Here goes the segmentation code

        # Apply the model and create a segmentation map
        if self.inference_main.model is not None:
            result = inference_model(self.inference_main.model, color_image)
            seg_image = self.inference_main.show_result(color_image, result, opacity=0.5)

        h, w, ch = seg_image.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(seg_image.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.changePixmap.emit(p)

    # def run_segmentation(self, color_image):
    #     # Here goes the segmentation code
    def connect_camera(self, camera_name):
        with self.lock:
            try:
                self.pipeline.start(self.config)
                self.is_connected = True
                return True
            except RuntimeError as e:
                QMessageBox.information(self, "Connection failed", "Could not connect to the selected camera: {}".format(e))

    def disconnect_camera(self):
        with self.lock:
            if self.is_connected:
                self.pipeline.stop()
                self.is_connected = False