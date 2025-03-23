from ultralytics import YOLO
import cv2

# Load the YOLO model
model = YOLO("v1 (1).pt")  # Your custom YOLO model

# Open the webcam (0 is typically the default webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Process frames from the webcam
while True:
    ret, frame = cap.read()  # Read a frame
    if not ret:
        print("Error: Failed to read frame.")
        break

    # Run YOLO inference on the frame
    results = model.predict(source=frame, show=True, conf=0.5)  # show=True displays using OpenCV internally

    # If you want to access bounding boxes, etc., you can iterate like this:
    for result in results:
        boxes = result.boxes
        # Optional: print boxes if needed
        # print(boxes.xyxy)  # Example: prints xyxy coordinates

    # Press 'q' to break the loop and close the webcam
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
