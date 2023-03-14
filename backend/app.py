import threading
from queue import Queue

import cv2
from flask import Flask, Response

capture = cv2.VideoCapture(0)
send_front = Queue(maxsize=256)
front_flag = False


def get_camera_frame():
    while True:
        ret, frame = capture.read()
        if ret:
            if front_flag:
                send_front.put(frame)


app = Flask(__name__)

capture_thr = threading.Thread(target=get_camera_frame, daemon=True)
capture_thr.start()


@app.route("/")
def index():
    return "Hello World!"


@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        global front_flag
        front_flag = True
        while True:
            try:
                frame = send_front.get(block=False)
                ret, frame = cv2.imencode(".jpg", frame)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + bytearray(frame) + b"\r\n"
                )
            except:
                pass

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
