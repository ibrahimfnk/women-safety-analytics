import cv2
import mediapipe as mp
import numpy as np


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

mp_drawing = mp.solutions.drawing_utils

def detect_distress_gesture(hand_landmarks):
    
 
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    
   
    if (thumb_tip.x < index_mcp.x and 
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y > index_mcp.y and 
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y > pinky_mcp.y):
        return True
    return False

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

       
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

      
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
               
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
              
                if detect_distress_gesture(hand_landmarks):
                    cv2.putText(frame, "Distress Signal Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # Trigger alert (e.g., sound, notification, etc.)
                    print("Alert: Distress Gesture Detected!")

        # Display the frame
        cv2.imshow('Hand Gesture Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
