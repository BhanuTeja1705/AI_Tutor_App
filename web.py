import cv2
import google.generativeai as genai
from PIL import Image
import pyttsx3
import speech_recognition as sr

# === Initialize Gemini API ===
GOOGLE_API_KEY = "AIzaSyAOz1lt8GWmd8T5J8p5Ldr-_yzkb-vyAVI"  # Replace with your actual API key if needed
genai.configure(api_key=GOOGLE_API_KEY)

# Using the latest Gemini model that supports multimodal input (text + image)
model_name = "models/gemini-1.5-pro-latest"

# === Text-to-Speech Setup ===
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # You can change the voice if you want
engine.setProperty('rate', 150)  # Speed of speech

def speak(text):
    """Convert text to speech."""
    print(f"\nAI: {text}\n")
    engine.say(text)
    engine.runAndWait()

# === Speech Recognition Setup ===
recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen():
    """Listen for voice input and return text."""
    with mic as source:
        print("Listening... (Ask your question)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand your speech.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

# === Capture Image from Webcam ===
def capture_image():
    """Capture an image from the webcam and save it."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Press SPACE to capture the image.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        cv2.imshow('Webcam - Press SPACE to capture', frame)

        key = cv2.waitKey(1)
        if key % 256 == 32:  # SPACE pressed
            img_name = "captured_image.jpg"
            cv2.imwrite(img_name, frame)
            print(f"Image captured and saved as {img_name}")
            break
        elif key % 256 == 27:  # ESC pressed
            print("Escape hit, closing...")
            cap.release()
            cv2.destroyAllWindows()
            exit()

    cap.release()
    cv2.destroyAllWindows()
    return img_name

# === Main Program ===
if __name__ == "__main__":
    print("===== Welcome to the Voice Image Q&A Assistant =====")
    speak("Welcome to the Voice Image Question and Answer Assistant.")

    # Step 1: Capture Image
    image_path = capture_image()

    # Step 2: Open and resize the image (optional for efficiency)
    im = Image.open(image_path)
    im.thumbnail([1024, 1024], Image.Resampling.LANCZOS)

    # Step 3: Convert image to bytes (inline data format for Gemini)
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()

    # Step 4: Create Gemini model instance
    model = genai.GenerativeModel(model_name)

    # Step 5: Start Voice Q&A loop
    speak("Image captured. You can now ask questions about the image.")
    print("Say 'exit' anytime to quit.\n")

    while True:
        # Listen for a voice question
        question = listen()

        if question is None:
            continue  # Ask again
        if question.lower() == "exit":
            speak("Goodbye! Exiting now.")
            break

        # Generate content using Gemini multimodal input (text + image)
        try:
            response = model.generate_content(
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": question},
                            {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                        ]
                    }
                ]
            )

            # Get the AI's answer and speak it
            answer = response.text
            speak(answer)

        except Exception as e:
            print(f"Error: {e}")
            speak("Sorry, there was an error processing your request.")
