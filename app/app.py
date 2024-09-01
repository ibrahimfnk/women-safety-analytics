from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit
import cv2
import json
import os
import base64
import time
import csv
import numpy as np

from ultralytics import YOLO


# Open CSV file for writing
csv_file_path = 'gender_counts.csv'
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Average Male Count', 'Average Female Count'])

#Load config
#with open('config.json') as config_file:
#    config = json.load(config_file)

# Get the directory of the current script
#script_dir = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
socketio = SocketIO(app)

# Load YOLOv8 model for face detection
yolo_model = YOLO(r'..\ml\models_new\yolov8x_person_face.pt')  # Ensure this model is only for face detection

# Load gender classification model (OpenCV DNN)
genderProto = r"..\ml\models_new\gender_deploy.prototxt"
genderModel = r"..\ml\models_new\gender_net.caffemodel"
genderNet = cv2.dnn.readNet(genderModel, genderProto)

genderList = ['Male', 'Female']

def detect_faces_yolo(frame):
    results = yolo_model(frame)
    boxes = []
    for result in results:
        for det in result.boxes:
            if det.conf > 0.5:
                x1, y1, x2, y2 = map(int, det.xyxy[0].tolist())
                boxes.append([x1, y1, x2, y2])
    return boxes

def classify_gender(genderNet, faceImage, genderList):
    blob = cv2.dnn.blobFromImage(faceImage, scalefactor=1, size=(227, 227),
                                mean=(78.4263377603, 87.7689143744, 114.895847746), crop=False)
    genderNet.setInput(blob)
    genderPrediction = genderNet.forward()
    gender = genderList[genderPrediction[0].argmax()]
    return gender



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@socketio.on('connect')
def handle_connect():
    print("client connected")

@socketio.on('start_video')
def handle_video():
    cap = cv2.VideoCapture('exx4.mp4')

    if not cap.isOpened():
        emit('error', {'message': 'Error: Could not open video.'})
        return
    
    alert_start_time = None
    alert_duration = 1  # Duration in seconds
    global last_record_time
    record_interval = 5
    last_record_time = time.time()  # Initialize last_record_time here
    male_counts = []
    female_counts = []
    

    while True:
        ret, frame = cap.read()
        if not ret:
            emit('error', {'message': 'Error: Failed to capture frame.'})
            break

        male_count = 0
        female_count = 0

        face_boxes = detect_faces_yolo(frame)

        for face_box in face_boxes:
            fx1, fy1, fx2, fy2 = face_box
            detected_face_box = frame[fy1:fy2, fx1:fx2]

            if detected_face_box.size > 0:
                gender = classify_gender(genderNet, detected_face_box, genderList)

                if gender == 'Male':
                    male_count += 1
                    color = (255, 0, 0)  # Blue for Male
                else:
                    female_count += 1
                    color = (0, 0, 255)  # Red for Female

                cv2.rectangle(frame, (fx1, fy1), (fx2, fy2), color, 2)
                cv2.putText(frame, gender, (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Collect counts
        male_counts.append(male_count)
        female_counts.append(female_count)

        current_time = time.time()

        if female_count < male_count:  # Adjust the threshold as needed
            if alert_start_time is None:
                alert_start_time = time.time()  # Start the timer
            elif time.time() - alert_start_time >= alert_duration:
                # Apply red overlay to the frame
                overlay = frame.copy()
                overlay[:] = [0, 0, 255]  # Red color
                alpha = 0.3  # Transparency factor
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

                # Emit alert to the client
                socketio.emit('alert', {'message': 'Female in danger!'})

        else:
            alert_start_time = None #Reset alert timer

        # Check if 5 seconds have passed
        if current_time - last_record_time >= record_interval:
            avg_male_count = np.mean(male_counts)/2 if male_counts else 0
            avg_female_count = np.mean(female_counts)/2 if female_counts else 0

            with open(csv_file_path, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), avg_male_count, avg_female_count])

            # Reset for the next interval
            male_counts = []
            female_counts = []
            last_record_time = current_time

        # Encode the frame to send to the client
        _, buffer = cv2.imencode('.jpg', frame)
        frame_encoded = base64.b64encode(buffer).decode('utf-8')

        # Emit the frame and the counts to the client
        socketio.emit('video_frame', frame_encoded)
        socketio.emit('update_counts', {'male_count': round(male_count/2), 'female_count': round(female_count/2)})

    cap.release()


if __name__ == "__main__":
    socketio.run(app, debug=True)