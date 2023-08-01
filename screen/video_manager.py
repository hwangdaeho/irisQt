from PyQt5.QtCore import QThread, QTimer, QMutex, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox
import pyrealsense2 as rs
import numpy as np
import cv2
class VideoManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.video_thread = VideoThread()
        # add necessary setup code here

    def get_video_thread(self):
        return self.video_thread



class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)
    # inference 에서 사용함
    changePixmapRaw = pyqtSignal(QImage)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mutex = QMutex()  # Add a mutex
        self.is_recording = False  # Add a flag for recording
        self.is_connected = False
        self.video_writer = None  # Add a video writer
        self.timer = QTimer()  # Add a timer
        self.timer.timeout.connect(self.update_frame)  # Connect the timer timeout signal to the update_frame method
        self.timer.start(1000 / 30)  # Start the timer to call update_frame 30 times per second
        self.pipeline = rs.pipeline()
        self.config = rs.config()


    def update_frame(self):
        self.mutex.lock()  # Lock the mutex
        is_connected = self.is_connected  # Store the flag value in a local variable
        is_recording = self.is_recording  # Store the flag value in a local variable
        self.mutex.unlock()  # Unlock the mutex

        if is_connected:
            frames = self.pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                return

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


    def get_is_recording(self):
        self.mutex.lock()  # Lock the mutex
        is_recording = self.is_recording
        self.mutex.unlock()  # Unlock the mutex
        return is_recording


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