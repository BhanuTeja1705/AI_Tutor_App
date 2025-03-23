import streamlit as st
import cv2
from PIL import Image
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai

# === CONFIGURATION ===
GOOGLE_API_KEY = "AIzaSyAOz1lt8GWmd8T5J8p5Ldr-_yzkb-vyAVI"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

model_name = "models/gemini-1.5-pro-latest"

# === TEXT-TO-SPEECH ===
engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(text):
    """Speaks the given text."""
    engine.say(text)
    engine.runAndWait()


# === VOICE-TO-TEXT ===
recognizer = sr.Recognizer()


def listen():
    """Listen and return the user's voice input as text."""
    with sr.Microphone() as source:
        st.info("Listening... Please ask your question!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        st.error(f"Request error: {e}")
        return None


# === IMAGE CAPTURE ===
def capture_image():
    """Capture an image from the webcam."""
    cap = cv2.VideoCapture(0)
    st.info("Press 'SPACE' to capture the image. Press 'ESC' to exit.")

    img_name = None
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to grab frame.")
            break

        cv2.imshow("Webcam - Press SPACE to capture, ESC to exit", frame)

        key = cv2.waitKey(1)
        if key % 256 == 32:  # SPACE pressed
            img_name = "captured_image.jpg"
            cv2.imwrite(img_name, frame)
            st.success(f"Image captured as {img_name}")
            break
        elif key % 256 == 27:  # ESC pressed
            st.warning("ESC pressed, closing camera.")
            break

    cap.release()
    cv2.destroyAllWindows()

    return img_name


# === GEMINI AI CALL ===
def ask_gemini(question, image_path):
    """Send the question and image to Gemini AI and return the answer."""
    try:
        model = genai.GenerativeModel(model_name)

        with open(image_path, "rb") as img_file:
            image_data = img_file.read()

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

        return response.text

    except Exception as e:
        st.error(f"Error communicating with Gemini AI: {e}")
        return "Sorry, there was an error."


# === STREAMLIT APP ===
def main():
    st.title("📷 Voice Controlled Image Q&A 🤖 (Streamlit Edition)")
    st.write("1. Capture an image.\n2. Ask a question via voice.\n3. AI will answer and speak it out!")

    # SESSION STATES
    if 'image_path' not in st.session_state:
        st.session_state.image_path = None

    # === Capture Image ===
    if st.button("📸 Capture Image"):
        image_path = capture_image()
        if image_path:
            st.session_state.image_path = image_path
            st.image(image_path, caption="Captured Image", use_column_width=True)

    # === Ask Question by Voice ===
    if st.button("🎤 Ask a Question (Voice)"):
        if not st.session_state.image_path:
            st.warning("Please capture an image first!")
        else:
            question = listen()
            if question:
                st.info("Sending question to Gemini AI...")
                answer = ask_gemini(question, st.session_state.image_path)
                st.success(f"AI Answer: {answer}")
                speak(answer)

    # === Exit ===
    if st.button("❌ Exit"):
        speak("Exiting the app. Goodbye!")
        st.stop()


# === RUN STREAMLIT APP ===
if __name__ == "__main__":
    main()
