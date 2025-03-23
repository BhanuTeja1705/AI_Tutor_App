import cv2
import mediapipe as mp
import pyautogui  # For simulating key presses
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Delay to give time to switch to your browser game window
print("You have 5 seconds to switch to your browser game window...")
time.sleep(5)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    fists = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            x = int(wrist.x * frame.shape[1])
            y = int(wrist.y * frame.shape[0])
            fists.append((x, y))

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    if len(fists) == 2:
        # Sort fists from left to right
        fists.sort()
        left_fist, right_fist = fists[0], fists[1]

        # Steering control
        y_diff = right_fist[1] - left_fist[1]

        if y_diff > 40:
            print("Steer Right")
            pyautogui.keyDown('d')
            pyautogui.keyUp('a')
        elif y_diff < -40:
            print("Steer Left")
            pyautogui.keyDown('a')
            pyautogui.keyUp('d')
        else:
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')

        # Speed control
        avg_y = (left_fist[1] + right_fist[1]) / 2
        center_y = frame.shape[0] / 2

        if avg_y < center_y - 50:
            print("Accelerate")
            pyautogui.keyDown('w')
            pyautogui.keyUp('s')
        elif avg_y > center_y + 50:
            print("Reverse")
            pyautogui.keyDown('s')
            pyautogui.keyUp('w')
        else:
            pyautogui.keyUp('w')
            pyautogui.keyUp('s')

    else:
        # No hands detected, release all keys
        pyautogui.keyUp('w')
        pyautogui.keyUp('s')
        pyautogui.keyUp('a')
        pyautogui.keyUp('d')

    # Show camera feed
    cv2.imshow("Hand Tracking Control", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
