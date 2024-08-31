import cv2
import numpy as np
from ultralytics import YOLO
import time
import csv

# Load YOLOv8 model for face detection
yolo_model = YOLO(r'models_new\yolov8x_person_face.pt')  # Ensure this model is only for face detection

# Load gender classification model (OpenCV DNN)
genderProto = r"models_new\gender_deploy.prototxt"
genderModel = r"models_new\gender_net.caffemodel"
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

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cv2.namedWindow('Gender Classification', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Gender Classification', frame_width, frame_height)

# Initialize timer variables
alert_start_time = None
alert_duration = 1  # Duration in seconds
last_record_time = time.time()
record_interval = 5  # Interval to record average counts
male_counts = []
female_counts = []

# Open CSV file for writing
csv_file = open('gender_counts.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time', 'Average Male Count', 'Average Female Count'])

while True:
    ret, inputImage = cap.read()
    if not ret:
        print("Error: Failed to capture frame or end of video.")
        break

    # Initialize gender counters
    male_count = 0
    female_count = 0

    # Detect faces
    face_boxes = detect_faces_yolo(inputImage)

    # Clear previous rectangles and text from the frame
    for face_box in face_boxes:
        fx1, fy1, fx2, fy2 = face_box

        if fx2 - fx1 > 0 and fy2 - fy1 > 0:
            detected_face_box = inputImage[fy1:fy2, fx1:fx2]

            if detected_face_box.size > 0:
                gender = classify_gender(genderNet, detected_face_box, genderList)

                if gender == 'Male':
                    male_count += 1
                    color = (255, 0, 0)  # Blue for Male
                else:
                    female_count += 1
                    color = (0, 0, 255)  # Red for Female

                cv2.rectangle(inputImage, (fx1, fy1), (fx2, fy2), color, 2)
                cv2.putText(inputImage, gender, (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Display male and female count on the frame at the top-left corner
    cv2.putText(inputImage, f'Male Count: {round(male_count/2)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(inputImage, f'Female Count: {round(female_count/2)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Check for specific conditions
    if female_count == 1 and male_count > 5:  # Adjust the threshold as needed
        if alert_start_time is None:
            alert_start_time = time.time()  # Start the timer
        elif time.time() - alert_start_time >= alert_duration:
            # Apply red overlay to the frame
            overlay = inputImage.copy()
            overlay[:] = [0, 0, 255]  # Red color
            alpha = 0.3  # Transparency factor
            cv2.addWeighted(overlay, alpha, inputImage, 1 - alpha, 0, inputImage)

            cv2.putText(inputImage, 'Alert: Single Woman Among Many Men', (10, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        alert_start_time = None  # Reset the timer if the condition is not met

    # Record average counts every 5 seconds
    current_time = time.time()
    if current_time - last_record_time >= record_interval:
        avg_male_count = np.mean(male_counts) if male_counts else 0
        avg_female_count = np.mean(female_counts) if female_counts else 0
        csv_writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), avg_male_count, avg_female_count])
        
        # Reset counters and timer
        male_counts = []
        female_counts = []
        last_record_time = current_time

    # Store current counts for averaging
    male_counts.append(male_count/2)
    female_counts.append(female_count/2)

    cv2.imshow('Gender Classification', inputImage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
csv_file.close()
