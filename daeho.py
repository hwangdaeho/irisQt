from flask import Flask, render_template, Response
import cv2
import pyrealsense2 as rs
import numpy as np

app = Flask(__name__)

pipeline = rs.pipeline()

# Create a config object
config = rs.config()

# Tell config that we will use a color image from RealSense D400 series
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

def get_frame():
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    if not color_frame:
        return None
    else:
        color_image = np.asanyarray(color_frame.get_data())
        ret, jpeg = cv2.imencode('.jpg', color_image)
        return jpeg.tobytes()

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        frame = get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
