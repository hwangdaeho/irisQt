from PyQt5.QtWidgets import (QWidget, QStackedWidget, QLabel, QVBoxLayout, QToolButton,
                             QLineEdit, QPushButton, QHBoxLayout, QGridLayout, QMessageBox, QSlider)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QIcon, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize, QTimer, QMutex
from screen.calibration.step.step1 import GuideScreen
import socket
from pynput.mouse import Listener as MouseListener
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QInputDialog
# import threading
from urx import Robot
import numpy as np
import time
import math
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
import pyrealsense2 as rs
import sys
class CalibrationMain(QWidget):
    def __init__(self, parent=None, stacked_widget=None, main_window=None):
        super().__init__(parent)

        self.ip_address = None
        self.check_connection_thread = None
        self.connection_circle = None  # 새로운 변수 추가
        self.connection_label = None  # 새로운 변수 추가
        self.is_connected = False  # 로봇이 연결되었는지
        self.camera_connected = False
        self.folder_created = False
        self.buttons = []  # Button list
        self.camera_buttons = []
        # self.setup_emergency_stop()
        # Set up layouts
        main_layout = QHBoxLayout()
        main_left_layout = QVBoxLayout()
        main_right_layout = QVBoxLayout()
        main_right_layout.setAlignment(Qt.AlignCenter)
        # Set up left panel
        self.setup_left_panel(main_left_layout)
        self.update_camera_button_states()
        # Set up right panel
        self.setup_right_panel(main_right_layout)

        # Add left and right panels to main layout
        main_layout.addLayout(main_left_layout)
        main_layout.addLayout(main_right_layout)
        self.setLayout(main_layout)

        self.pi=math.pi
        self.VELOCITY = 5
        self.ACCELERATION = self.VELOCITY * 2
        self.move_val = self.VELOCITY / 100
        self.rot_val = self.VELOCITY / 100

        self.update_button_states()

        self.thread = VideoThread()
        self.thread.changePixmap.connect(self.setImage)

        # Start the video thread
        self.thread.start()
    def setup_left_panel(self, layout):
        layout.addSpacing(50)

        # This is where the image will go
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)  # Align the image to the center
        self.show_placeholder_image()
        layout.addWidget(self.image_label)

        button_layout = self.setup_button_layout()
        layout.addLayout(button_layout)
        layout.setSpacing(0)

    def setup_right_panel(self, layout):
        layout.addSpacing(0)
        ip_text = QHBoxLayout()
        ip_text.setContentsMargins(0, 0, 0, 0)  # No margins
        ip_label = QLabel("IP 연결")
        ip_label.setFixedHeight(30)
        ip_text.addWidget(ip_label)

        ip_input_line = QHBoxLayout()
        ip_input_line.setContentsMargins(0, 0, 0, 0)  # No margins
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("IP 주소 입력")
        self.connect_button = QPushButton()
        self.connect_button.setStyleSheet('background-color: #B50039; border: none; color: white; font-size:15px')
        self.connect_button.setFixedSize(QSize(80, 30))  # Set fixed size for the button
        self.connect_button.setText('연결')
        self.connect_button.clicked.connect(self.on_connect_button_clicked)
        ip_input_line.addWidget(self.ip_input)
        ip_input_line.addWidget(self.connect_button)

        layout.addLayout(ip_text)
        layout.addLayout(ip_input_line)

        # Create a widget that will contain the layout
        right_sub_widget = QWidget()

        # Set the widget's background color
        right_sub_widget.setStyleSheet("background-color: #393939;")
        right_sub_widget.setFixedHeight(550)

        # Create the layout
        right_sub_layout = QVBoxLayout()

        right_sub_layout.addWidget(self.connection_layout())
        # Then add the text with a black background
        black_background_text = QLabel("Your text here")
        black_background_text.setStyleSheet("background-color: black; color: white;")
        black_background_text.setFixedHeight(170)
        right_sub_layout.addWidget(black_background_text)

        right_sub_layout.addLayout(self.grid_header())

        # Finally add the grid layout
        grid_layout = self.setup_grid_layout()
        right_sub_layout.addLayout(grid_layout)
        # Assign the layout to the widget

        right_sub_layout.addLayout(self.speed_header())
        slider = QSlider(Qt.Horizontal)  # Create a horizontal slider
        slider.setMinimum(1)  # Set the minimum value to 1
        slider.setMaximum(5)  # Set the maximum value to 100
        slider.setValue(5)  # Set the initial value to 50 (in the middle)
        slider.valueChanged.connect(self.handle_slider_value_changed)
        right_sub_layout.addWidget(slider)  # Add the slider to the layout
        right_sub_widget.setLayout(right_sub_layout)
        # Add the widget to the main layout
        layout.addWidget(right_sub_widget)

    def handle_slider_value_changed(self, value):
        self.VELOCITY = value
        self.ACCELERATION = self.VELOCITY * 2
        self.move_val = self.VELOCITY / 100
        self.rot_val = self.VELOCITY / 100
        print(self.VELOCITY)


    def connection_layout(self):
        # Create a horizontal layout
        connection_line = QHBoxLayout()
        connection_line.setSpacing(3)
        # Create a label
        self.connection_label = QLabel("Connection Fail")  # 수정된 부분
        self.connection_label.setStyleSheet('color: white;')
        self.connection_label.setFixedHeight(25)
        self.connection_label.setAlignment(Qt.AlignTop)
        # Create a circle widget
        self.connection_circle = CircleWidget("red")  # 수정된 부분
        self.connection_circle.setFixedHeight(10)  # adjust the size as needed
        self.connection_circle.setFixedWidth(10)  # adjust the size as needed

        # Add circle widget and label to the layout
        connection_line.addWidget(self.connection_circle)
        connection_line.addWidget(self.connection_label)
        connection_line.addStretch(1)  # push everything to the left

        # Create a new widget to hold the layout
        connection_widget = QWidget()
        connection_widget.setFixedHeight(30)
        connection_widget.setLayout(connection_line)

        return connection_widget

    def set_connection_state(self, connected):  # 새로운 메서드 추가
        self.is_connected = connected
        if connected:
            self.connection_circle.setColor("green")
            self.connection_label.setText("Connection OK")
        else:
            self.connection_circle.setColor("red")
            self.connection_label.setText("Connection Fail")
        self.update_button_states()

    def setup_emergency_stop(self):
        self.shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        self.shortcut.activated.connect(self.emergency_stop)

    def emergency_stop(self):
        try:
            self.robot.secmon.close()  # Emergency stop the robot
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop the robot: {str(e)}")

    def on_connect_button_clicked(self):
        ...
        self.start_check_connection_thread()

    def start_check_connection_thread(self):
        self.check_connection_thread = QThread(target=self.check_connection)
        self.check_connection_thread.start()

    def check_connection(self):
        while True:
            if not self.robot.is_program_running():
                QMessageBox.critical(self, "Error", "Lost connection to the robot.")
                break

            time.sleep(1)  # Check connection every second
    def setup_grid_layout(self):

        grid_layout = QGridLayout()

        # Specify which positions to have buttons and their associated image paths

        button_positions = {
            (0, 0): { "image": ":image/Orientation/button-down.svg", "start_function": self.start_move_plus_Z, "stop_function": self.stop_move_plus_Z, "icon_size": QSize(80, 80) },
            (0, 2): { "image": ":image/Orientation/button-up.svg", "start_function": self.start_move_minus_Z, "stop_function": self.stop_move_minus_Z, "icon_size": QSize(80, 80)},

            (0, 4): { "image": ":image/position/turn-left.svg", "start_function": self.start_rotate_plus_Z, "stop_function": self.stop_rotate_plus_Z, "icon_size": QSize(80, 80)},
            (0, 6): { "image": ":image/position/turn-right.svg", "start_function": self.start_rotate_minus_Z, "stop_function": self.stop_rotate_minus_Z, "icon_size": QSize(80, 80)},

            (1, 1): { "image": ":image/position/arrow-up.svg", "start_function": self.start_move_minus_X, "stop_function": self.stop_move_minus_X, "icon_size": QSize(80, 40) },
            (1, 5): { "image": ":image/Orientation/arrow-up.svg", "start_function": self.start_rotate_plus_Y, "stop_function": self.stop_rotate_plus_Y, "icon_size": QSize(80, 40)},

            (2, 0): { "image": ":image/position/arrow-left.svg", "start_function": self.start_move_minus_Y, "stop_function": self.stop_move_minus_Y, "icon_size": QSize(40, 96), "alignment": Qt.AlignRight},
            (2, 2): { "image": ":image/position/arrow-right.svg", "start_function": self.start_move_plus_Y, "stop_function": self.stop_move_plus_Y, "icon_size": QSize(40, 96) },

            (2, 4): { "image": ":image/Orientation/arrow-left.svg", "start_function": self.start_rotate_plus_X, "stop_function": self.stop_rotate_plus_X, "icon_size": QSize(40, 96), "alignment": Qt.AlignRight},
            (2, 6): { "image": ":image/Orientation/arrow-right.svg", "start_function": self.start_rotate_minus_X, "stop_function": self.stop_rotate_minus_X, "icon_size": QSize(40, 96)},

            (3, 1): { "image": ":image/position/arrow-down.svg", "start_function": self.start_move_plus_X, "stop_function": self.stop_move_plus_X, "icon_size": QSize(80, 40)},
            (3, 3): { "image": ":image/position/button-Free.svg", "start_function": self.start_move_plus_X, "stop_function": self.stop_move_plus_X, "icon_size": QSize(80, 40)},
            (3, 5): { "image": ":image/Orientation/arrow-down.svg", "start_function": self.start_rotate_minus_Y, "stop_function": self.stop_rotate_minus_Y, "icon_size": QSize(80, 40)},
        }


        # Create a 4x6 grid of buttons
        for i in range(4):
            for j in range(7):
                if (i, j) in button_positions:
                    button_info = button_positions[(i, j)]
                    button = self.create_button(button_info, button_info['icon_size'])
                    if 'start_function' in button_info and 'stop_function' in button_info:
                        button.pressed.connect(button_info['start_function'])
                        button.released.connect(button_info['stop_function'])
                    grid_layout.addWidget(button, i, j)
                    if "alignment" in button_info:
                        grid_layout.setAlignment(button, button_info["alignment"])

        # grid_layout.setColumnStretch(0, 3)

        grid_layout.setSpacing(0)
        grid_layout.setHorizontalSpacing(0)
        grid_layout.setVerticalSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        return grid_layout
    def grid_header(self):
        # Create a QVBoxLayout for the TCP Position icon and text
        tcp_position_layout = QHBoxLayout()
        tcp_position_layout.setAlignment(Qt.AlignLeft)  # Align the image to the center
        # Create a label for the icon
        tcp_position_icon_label = QLabel()
        pixmap = QPixmap(":image/position/TCP-Position.svg")
        tcp_position_icon_label.setPixmap(pixmap)

        # Create a label for the text
        tcp_position_text_label = QLabel("TCP Position")
        tcp_position_text_label.setStyleSheet("color:white")
        # Add the icon and text labels to the layout
        tcp_position_layout.addWidget(tcp_position_icon_label)
        tcp_position_layout.addWidget(tcp_position_text_label)

        # Do the same for the TCP Orientation icon and text
        tcp_orientation_layout = QHBoxLayout()
        tcp_orientation_layout.setAlignment(Qt.AlignLeft)  # Align the image to the center
        tcp_orientation_icon_label = QLabel()
        pixmap = QPixmap(":image/Orientation/TCP-Orientation.svg")
        tcp_orientation_icon_label.setPixmap(pixmap)

        tcp_orientation_text_label = QLabel("TCP Orientation")
        tcp_orientation_text_label.setStyleSheet("color:white")
        tcp_orientation_layout.addWidget(tcp_orientation_icon_label)
        tcp_orientation_layout.addWidget(tcp_orientation_text_label)

        # Create a QHBoxLayout to hold the two QVBoxLayouts
        grid_header_layout = QHBoxLayout()
        # Add the QVBoxLayouts to the QHBoxLayout
        grid_header_layout.addLayout(tcp_position_layout)
        grid_header_layout.addLayout(tcp_orientation_layout)

        return grid_header_layout
    def speed_header(self):
        # Create a QVBoxLayout for the TCP Position icon and text
        tcp_position_layout = QHBoxLayout()
        tcp_position_layout.setAlignment(Qt.AlignLeft)  # Align the image to the center
        # Create a label for the icon
        tcp_position_icon_label = QLabel()
        pixmap = QPixmap(":image/Speed.svg")
        tcp_position_icon_label.setPixmap(pixmap)

        # Create a label for the text
        tcp_position_text_label = QLabel("Speed")
        tcp_position_text_label.setStyleSheet("color:white")
        # Add the icon and text labels to the layout
        tcp_position_layout.addWidget(tcp_position_icon_label)
        tcp_position_layout.addWidget(tcp_position_text_label)

        return tcp_position_layout

    def setup_button_layout(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)  # Set the space between the buttons
        button_layout.setAlignment(Qt.AlignCenter)  # Align the image to the center
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_names = ["카메라 연결", "경로설정", "이미지 저장", "영상 저장",  "데이터 보기"]
        self.enabled_icons = [":image/camera.svg", ":image/folder-add.svg", ":image/gallery.svg", ":image/video.svg", ":image/video-octagon.svg"]
        self.disabled_icons = [":image/camera2.svg", ":image/folder-add2.svg", ":image/gallery2.svg", ":image/video2.svg", ":image/video-octagon2.svg"]

        # Create the buttons and add them to the layout
        for i, name in enumerate(button_names):
            button = self.create_tool_button(name, self.enabled_icons[i])

            self.camera_buttons.append(button)
            button_layout.addWidget(button)
        self.camera_buttons[0].clicked.connect(self.connect_camera)  # '카메라 연결' 버튼을 connect_camera 함수에 연결
        self.camera_buttons[1].clicked.connect(self.create_folder)  # '카메라 연결' 버튼을 connect_camera 함수에 연결
        return button_layout

    def create_folder(self):
        if self.camera_connected:  # Only allow to create a folder when the camera is connected
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            options |= QFileDialog.DontUseNativeDialog
            folder_path = QFileDialog.getExistingDirectory(self, 'Select Directory',options=options)
            if folder_path:
                self.folder_path = folder_path
                self.folder_created = True
                self.update_button_states()  # Update button states
    def create_button(self, button_info, icon_size):

        button = QToolButton()

        image = QImage(button_info["image"])
        button.setStyleSheet("border:none")
        button.setCursor(Qt.PointingHandCursor)
        aspect_ratio = image.width() / image.height()

        # We assume that the button size is set here, for example to 200x120.
        # button.setFixedSize(QSize(80, 80))

        button.setIcon(QIcon(QPixmap.fromImage(image)))
        button.setIconSize(icon_size)  # Set the icon size

        button.pressed.connect(button_info['start_function'])
        button.released.connect(button_info['stop_function'])
        self.buttons.append(button)  # Add button to list

        # button.clicked.connect(button_info["function"])  # Connect the button's clicked signal to the associated function

        return button
    def update_button_states(self):
        for button in self.buttons:
            button.setEnabled(self.is_connected)
    def set_connected(self, connected):
        self.is_connected = connected
        self.update_button_states()
    def create_tool_button(self, name, icon_path):
        button = QToolButton()
        button.setText(name)
        button.setStyleSheet('background-color: #2F2F2F; color: white; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the background to black and text to white
        button.setCursor(Qt.PointingHandCursor)
        button.setIcon(QIcon(icon_path))  # Set the icon
        button.setIconSize(QSize(24, 24))  # Set the icon size
        button.setFixedSize(QSize(128, 100))  # Set the button size
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        return button


    def show_placeholder_image(self):
        # Load your placeholder image
        placeholder = QImage(":image/null.png")
        # Display the placeholder image
        self.setImage(placeholder)

    def setImage(self, image):
        self.current_image = image
        self.image_label.setPixmap(QPixmap.fromImage(image))
        self.image_label.setContentsMargins(0, 0, 0, 0)

    def connect_camera(self):
        # If the camera is already connected, disconnect it
        if self.thread.is_connected:
            self.thread.disconnect_camera()
            self.camera_buttons[0].setText("카메라 연결")
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
                        self.camera_buttons[0].setText("연결 해제")  # Change the button text
                        self.camera_connected = True
            else:
                QMessageBox.information(self, "No cameras found", "No cameras were found. Please connect a camera and try again.")
                self.show_placeholder_image()  # Add this line

        self.update_camera_button_states()  # Update button states

    def update_camera_button_states(self):
        self.camera_buttons[0].setEnabled(True)  # '카메라 연결' button
        # self.camera_buttons[1].setEnabled(True)  # '카메라 연결' button
        # self.camera_buttons[2].setEnabled(True)  # '카메라 연결' button
        self.camera_buttons[1].setEnabled(self.camera_connected)  # '생성' button
        self.camera_buttons[2].setEnabled(self.camera_connected and self.folder_created)  # '이미지 저장' button
        self.camera_buttons[3].setEnabled(True)  # '카메라 연결' button
        # self.buttons[3].setEnabled(self.camera_connected and self.folder_created)  # '영상 저장' button

        # Update button colors
        for i, button in enumerate(self.camera_buttons):
            if button.isEnabled():
                button.setEnabled(True)
                button.setIcon(QIcon(self.enabled_icons[i]))  # Change this line
                button.setStyleSheet('background-color: #2F2F2F; color: white; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the enabled button color
            else:
                button.setEnabled(False)
                button.setIcon(QIcon(self.disabled_icons[i]))  # Change this line
                button.setStyleSheet('background-color: #2F2F2F; color: #525252; font-size:15px; padding: 19px 16px;border-top: 1.5px solid #2F2F2F;border-right: 1.5px solid #2F2F2F;border-bottom: 1.5px solid #2F2F2F;')  # Set the disabled button color

    # 로봇 연결했는지 안했는지
    def on_connect_button_clicked(self):
        if not self.is_connected:  # 연결 안된 상태라면 연결 시도
            ip_address = self.ip_input.text()  # Get the entered IP address

            try:
                # Try to connect to the robot at the specified IP address
                print("VELOCITY : ", self.VELOCITY)
                print("ACCELERATION : ", self.ACCELERATION)
                print("move_val : ", self.move_val)
                print("rot_val : ", self.rot_val)

                self.robot = Robot(ip_address)
                robot_pose = self.robot.getl()
                print(robot_pose)

                QMessageBox.information(self, "Success", f"Connected to the robot at {ip_address}")
                self.set_connection_state(True)
                self.is_connected = True  # 성공적으로 연결된 경우
                self.ip_address = ip_address
                self.connect_button.setText('해제')  # Button text 변경
                self.connect_button.disconnect()  # disconnect all slots
                self.connect_button.clicked.connect(self.on_disconnect_button_clicked)  # Button action 변경
                print("moving to initial pose")
                self.robot.movej((90*(self.pi/180), -90*(self.pi/180), -90*(self.pi/180), -90*(self.pi/180), 90*(self.pi/180), 0*(self.pi/180)), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False)
                print("Waiting 1s for end move")
                # time.sleep(1)
            except Exception as e:
                # If the connection failed, show an error message
                QMessageBox.critical(self, "Error", f"Failed to connect to the robot at {ip_address}: {str(e)}")
                self.set_connection_state(False)


    def on_disconnect_button_clicked(self):
        # 로봇 연결 해제 로직 작성
        # (코드 작성)
        self.robot.close()
        # listener.stop()
        self.is_connected = False  # 연결 해제 후
        self.connect_button.setText('연결')  # Button text 변경
        self.connect_button.disconnect()
        self.set_connection_state(False)
        self.connect_button.clicked.connect(self.on_connect_button_clicked)  # Button action 변경





    # 로봇 좌표 움직임 컨트롤러

    def start_move_minus_X(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_minus_X)
        self.timer.start(100)  # 100ms마다 반복 실행.
    def stop_move_minus_X(self):
        self.timer.stop()

    def start_move_plus_X(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_plus_X)
        self.timer.start(100)

    def stop_move_plus_X(self):
        self.timer.stop()

    def start_move_minus_Y(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_minus_Y)
        self.timer.start(100)

    def stop_move_minus_Y(self):
        self.timer.stop()

    def start_move_plus_Y(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_plus_Y)
        self.timer.start(100)

    def stop_move_plus_Y(self):
        self.timer.stop()

    def start_move_minus_Z(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_minus_Z)
        self.timer.start(100)

    def stop_move_minus_Z(self):
        self.timer.stop()

    def start_move_plus_Z(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_plus_Z)
        self.timer.start(100)

    def stop_move_plus_Z(self):
        self.timer.stop()

    def start_rotate_minus_X(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_minus_X)
        self.timer.start(100)

    def stop_rotate_minus_X(self):
        self.timer.stop()

    def start_rotate_plus_X(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_plus_X)
        self.timer.start(100)

    def stop_rotate_plus_X(self):
        self.timer.stop()

    def start_rotate_minus_Y(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_minus_Y)
        self.timer.start(100)

    def stop_rotate_minus_Y(self):
        self.timer.stop()

    def start_rotate_plus_Y(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_plus_Y)
        self.timer.start(100)

    def stop_rotate_plus_Y(self):
        self.timer.stop()

    def start_rotate_minus_Z(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_minus_Z)
        self.timer.start(100)

    def stop_rotate_minus_Z(self):
        self.timer.stop()

    def start_rotate_plus_Z(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_plus_Z)
        self.timer.start(100)

    def stop_rotate_plus_Z(self):
        self.timer.stop()


    def move_minus_X(self):
        print(-1*self.move_val)
        self.robot.movel((-1*self.move_val, 0, 0, 0, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, relative=True, wait=False)

    def move_plus_X(self):
        self.robot.movel((self.move_val, 0, 0, 0, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, relative=True, wait=False)

    def move_minus_Y(self):
        self.robot.movel((0, -1*self.move_val, 0, 0, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, relative=True, wait=False)

    def move_plus_Y(self):
        self.robot.movel((0, self.move_val, 0, 0, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, relative=True, wait=False)

    def move_minus_Z(self):
        self.robot.movel((0, 0, -1*self.move_val, 0, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, relative=True, wait=False)

    def move_plus_Z(self):
        self.robot.movel((0, 0, self.move_val, 0, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, relative=True, wait=False)

    def rotate_minus_X(self):
        self.robot.movel_tool((0, 0, 0, -1*self.rot_val, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False) # tool 기준

    def rotate_plus_X(self):
        self.robot.movel_tool((0, 0, 0, self.rot_val, 0, 0), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False) # tool 기준

    def rotate_minus_Y(self):
        self.robot.movel_tool((0, 0, 0, 0, -1*self.rot_val, 0), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False) # tool 기준

    def rotate_plus_Y(self):
        self.robot.movel_tool((0, 0, 0, 0, self.rot_val, 0), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False) # tool 기준

    def rotate_minus_Z(self):
        self.robot.movel_tool((0, 0, 0, 0, 0, -1*self.rot_val), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False) # tool 기준

    def rotate_plus_Z(self):
        self.robot.movel_tool((0, 0, 0, 0, 0, self.rot_val), acc=self.ACCELERATION, vel=self.VELOCITY, wait=False) # tool 기준

    def freedrive(self):
        print("change to freedive mode")
        freedrive_duration = 10 # freedrive 모드 유지 시간 (초)
        self.robot.set_freedrive(True)

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

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
        # is_recording = self.is_recording  # Store the flag value in a local variable
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
            # if is_recording and self.video_writer is not None:
            #     bgr_frame = cv2.cvtColor(rgbImage, cv2.COLOR_RGB2BGR)
            #     # If we are recording, write the frame into the video writer
            #     self.video_writer.write(bgr_frame)
    def disconnect_camera(self):
        self.mutex.lock()  # Lock the mutex
        if self.is_connected:
            self.pipeline.stop()
            self.is_connected = False  # Set this flag to False after stopping the pipeline
        self.mutex.unlock()  # Unlock the mutex
class CircleWidget(QWidget):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self._color = color

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setBrush(QColor(self._color))
        qp.drawEllipse(0, 0, self.width(), self.height())

    def setColor(self, color):
        self._color = color
        self.update()  # Notify the system that the widget needs to be redrawn