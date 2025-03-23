import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Gesture control settings
gesture_delay = 1  # seconds between actions
last_action_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not working")
        break

    # Flip image for natural control
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame for hand landmarks
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip position (landmark 8)
            x = int(hand_landmarks.landmark[8].x * w)
            y = int(hand_landmarks.landmark[8].y * h)

            # Draw circle on the tip for visualization
            cv2.circle(frame, (x, y), 15, (255, 0, 255), cv2.FILLED)

            # Display thresholds
            middle_left = w // 3
            middle_right = 2 * w // 3
            upper_threshold = h // 3
            lower_threshold = 2 * h // 3

            current_time = time.time()

            # Print position and thresholds for debugging
            print(f"X: {x}, Y: {y}, Left: {middle_left}, Right: {middle_right}, Up: {upper_threshold}, Down: {lower_threshold}")

            # Gesture detection with delay control
            if current_time - last_action_time > gesture_delay:
                if x < middle_left:
                    print("Move Left!")
                    pyautogui.press('left')
                    last_action_time = current_time
                elif x > middle_right:
                    print("Move Right!")
                    pyautogui.press('right')
                    last_action_time = current_time
                elif y < upper_threshold:
                    print("Jump!")
                    pyautogui.press('up')
                    last_action_time = current_time
                elif y > lower_threshold:
                    print("Slide Down!")
                    pyautogui.press('down')
                    last_action_time = current_time
                else:
                    print("Neutral Zone - No Action")

    # Display the frame
    cv2.imshow("Temple Run Hand Gesture Controller", frame)

    # Exit with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
