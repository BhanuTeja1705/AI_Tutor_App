from ultralytics import YOLO

# Load a model
model = YOLO("v1 (1).pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
results = model(["groupapples.jpg"])  # return a list of Results objects
 # return a list of Results objects

# Process results list
for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    result.show()  # display to screen
    result.save(filename="result.jpg")  # save to disk