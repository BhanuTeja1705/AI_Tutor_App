import pygame
import random
import time
import threading
import speech_recognition as sr
import math
import google.generativeai as genai
from gtts import gTTS
import os
import uuid
from tkinter import filedialog, Tk
from PIL import Image
import mimetypes
import cv2

# ==========================
# CONFIGURE YOUR GEMINI API KEY
# ==========================
genai.configure(api_key="AIzaSyDPAjI3VeKDVaQ_5LB61owH1uZJoiQjKiU")  # <--- Replace with your actual key

# ==========================
# Global Variables
# ==========================
current_expression = "neutral"
speaking = False
lip_animation_state = False
lip_last_switch = time.time()
lip_switch_interval = 0.2
loaded_image_path = None
lock = threading.Lock()

# Hand wave state
hand_waving = False
hand_wave_start = 0
hand_wave_duration = 2  # seconds

# ==========================
# Gemini Functions (unchanged)
# ==========================
def ask_gemini_text(prompt):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API (Text): {e}")
        return "Sorry, I couldn't get an answer right now."

def ask_gemini_with_image(prompt, image_path):
    if not image_path:
        return "No image loaded! Please load or capture an image first."
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "image/jpeg"
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
        image_part = {
            "mime_type": mime_type,
            "data": image_data
        }
        prompt = f"Here's an image. {prompt} Please analyze and provide a detailed answer."
        response = model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        print(f"Error with Gemini API (Image): {e}")
        return "Sorry, I couldn't answer about the image right now."

# ==========================
# Text-to-Speech Function (unchanged)
# ==========================
def speak_text(text, lang="en"):
    global speaking
    with lock:
        try:
            unique_id = str(uuid.uuid4())
            filename = f"response_{unique_id}.mp3"
            tts = gTTS(text=text, lang=lang)
            tts.save(filename)
            sound = pygame.mixer.Sound(filename)
            speaking = True
            sound.play()
            while pygame.mixer.get_busy():
                pygame.time.wait(100)
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            print(f"Error in TTS: {e}")
        finally:
            speaking = False

# ==========================
# Initialize Pygame and Mixer (unchanged)
# ==========================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 700  # Increased height for legs!
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rectangle Robot Face + Image QA + Camera + Hand Wave")

BLACK = (20, 20, 30)
DARK_GRAY = (40, 40, 60)
WHITE = (240, 240, 255)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
GREEN = (100, 255, 100)

expressions = {
    "happy": {"eye_color": CYAN, "mouth": "smile"},
    "sad": {"eye_color": CYAN, "mouth": "frown"},
    "angry": {"eye_color": RED, "mouth": "angry"},
    "surprised": {"eye_color": YELLOW, "mouth": "open"},
    "love": {"eye_color": PINK, "mouth": "heart"},
    "neutral": {"eye_color": CYAN, "mouth": "flat"},
}

# ==========================
# Drawing Functions (with body and legs added)
# ==========================
def draw_robot_body():
    # Draw body below the head
    body_x = 220
    body_y = 380
    body_width = 160
    body_height = 140
    pygame.draw.rect(screen, DARK_GRAY, (body_x, body_y, body_width, body_height), border_radius=20)

def draw_legs():
    # Left leg
    left_leg_x = 240
    leg_y = 520
    leg_width = 40
    leg_height = 100
    pygame.draw.rect(screen, DARK_GRAY, (left_leg_x, leg_y, leg_width, leg_height), border_radius=10)

    # Right leg
    right_leg_x = 320
    pygame.draw.rect(screen, DARK_GRAY, (right_leg_x, leg_y, leg_width, leg_height), border_radius=10)

def draw_robot_head():
    screen.fill((200, 200, 255))
    face_x, face_y, face_width, face_height = 180, 200, 240, 180
    outer_x, outer_y = face_x - 10, face_y - 10
    outer_width, outer_height = face_width + 20, face_height + 20
    pygame.draw.rect(screen, WHITE, (outer_x, outer_y, outer_width, outer_height), border_radius=30)
    pygame.draw.rect(screen, DARK_GRAY, (face_x, face_y, face_width, face_height), border_radius=20)

def draw_eyes(expression, blink_state):
    eye_color = expressions[expression]["eye_color"]
    left_eye_pos = (WIDTH // 2 - 50, 250)
    right_eye_pos = (WIDTH // 2 + 50, 250)
    eye_radius, pupil_radius = 20, 8
    if blink_state:
        pygame.draw.line(screen, eye_color, (left_eye_pos[0] - 15, left_eye_pos[1]),
                         (left_eye_pos[0] + 15, left_eye_pos[1]), 5)
        pygame.draw.line(screen, eye_color, (right_eye_pos[0] - 15, right_eye_pos[1]),
                         (right_eye_pos[0] + 15, right_eye_pos[1]), 5)
        return
    pygame.draw.circle(screen, eye_color, left_eye_pos, eye_radius)
    pygame.draw.circle(screen, eye_color, right_eye_pos, eye_radius)
    pygame.draw.circle(screen, BLACK, left_eye_pos, pupil_radius)
    pygame.draw.circle(screen, BLACK, right_eye_pos, pupil_radius)

def draw_mouth(expression):
    global lip_animation_state
    mouth_type = expressions[expression]["mouth"]
    mouth_center_x, mouth_y = WIDTH // 2, 310
    if speaking:
        mouth_type = "open" if lip_animation_state else "flat"
    if mouth_type == "smile":
        pygame.draw.arc(screen, CYAN, (mouth_center_x - 40, mouth_y - 10, 80, 40), math.pi, 2 * math.pi, 5)
    elif mouth_type == "frown":
        pygame.draw.arc(screen, CYAN, (mouth_center_x - 40, mouth_y, 80, 40), 0, math.pi, 5)
    elif mouth_type == "angry":
        pygame.draw.lines(screen, RED, False,
                          [(mouth_center_x - 30, mouth_y), (mouth_center_x - 10, mouth_y - 10),
                           (mouth_center_x + 10, mouth_y), (mouth_center_x + 30, mouth_y - 10)], 4)
    elif mouth_type == "open":
        pygame.draw.ellipse(screen, YELLOW, (mouth_center_x - 20, mouth_y, 40, 30))
    elif mouth_type == "heart":
        points = [(mouth_center_x, mouth_y + 10), (mouth_center_x - 20, mouth_y - 10),
                  (mouth_center_x + 20, mouth_y - 10)]
        pygame.draw.polygon(screen, PINK, points)
        pygame.draw.circle(screen, PINK, (mouth_center_x - 10, mouth_y - 10), 10)
        pygame.draw.circle(screen, PINK, (mouth_center_x + 10, mouth_y - 10), 10)
    elif mouth_type == "flat":
        pygame.draw.line(screen, CYAN, (mouth_center_x - 30, mouth_y + 10), (mouth_center_x + 30, mouth_y + 10), 5)

def draw_loaded_image(image_path):
    if image_path:
        try:
            img = pygame.image.load(image_path)
            img = pygame.transform.scale(img, (200, 200))
            screen.blit(img, (200, 20))
        except Exception as e:
            print(f"Error loading image on screen: {e}")

def draw_hand():
    # Right hand (waving)
    hand_x = 400
    base_y = 400
    amplitude = 20
    if hand_waving:
        wave_offset = amplitude * math.sin(10 * (time.time() - hand_wave_start))
    else:
        wave_offset = 0
    hand_y = base_y + wave_offset
    pygame.draw.rect(screen, DARK_GRAY, (hand_x, hand_y, 20, 60), border_radius=10)

    # Left hand (static)
    left_hand_x = 180
    left_hand_y = 400
    pygame.draw.rect(screen, DARK_GRAY, (left_hand_x, left_hand_y, 20, 60), border_radius=10)

# ==========================
# Image Loading Function (unchanged)
# ==========================
def load_image():
    global loaded_image_path
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        loaded_image_path = file_path
        print(f"📷 Image loaded: {loaded_image_path}")
    root.destroy()

# ==========================
# Camera Capture Function (unchanged)
# ==========================
def capture_image_from_camera():
    global loaded_image_path
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    print("📸 Camera opened! Press SPACE to capture or ESC to cancel.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
        cv2.imshow("Camera - Press SPACE to capture", frame)
        key = cv2.waitKey(1)
        if key % 256 == 27:
            print("🚪 Escape hit, closing camera.")
            break
        elif key % 256 == 32:
            filename = f"captured_{uuid.uuid4().hex}.jpg"
            cv2.imwrite(filename, frame)
            loaded_image_path = filename
            print(f"✅ Image captured and saved as {filename}")
            break
    cap.release()
    cv2.destroyAllWindows()

# ==========================
# Voice Listener Function (unchanged)
# ==========================
def listen_for_command():
    global current_expression, hand_waving, hand_wave_start
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            print("\n🎤 Say an expression (happy, sad, angry, surprised, love), or ask a question (mention 'image' if you want to ask about the loaded image):")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                print(f"🗣️ You said: {text}")
                if "hi" in text.lower() or "hello" in text.lower():
                    print("👋 Waving hand and saying hi!")
                    current_expression = "happy"
                    hand_waving = True
                    hand_wave_start = time.time()
                    speak_text("Hi there!", lang="en")
                    time.sleep(2)
                    hand_waving = False
                    continue
                if any(word in text.lower() for word in expressions.keys()):
                    for word in expressions.keys():
                        if word in text.lower():
                            current_expression = word
                            print(f"😎 Expression changed to: {current_expression}")
                            break
                    continue
                current_expression = "neutral"
                if any(keyword in text.lower() for keyword in ["image", "picture", "photo"]) and loaded_image_path:
                    print("🤖 Analyzing image with Gemini Vision...")
                    answer = ask_gemini_with_image(text, loaded_image_path)
                elif any(keyword in text.lower() for keyword in ["image", "picture", "photo"]):
                    answer = "No image loaded! Please load or capture an image first."
                else:
                    print("🤖 Thinking (Text)...")
                    answer = ask_gemini_text(text)
                print(f"🤖 Gemini says: {answer}")
                current_expression = "happy"
                speak_text(answer, lang="en")
            except sr.UnknownValueError:
                print("❌ Sorry, I didn't catch that.")
            except sr.RequestError as e:
                print(f"❌ Could not request results; {e}")

# ==========================
# Start Voice Listener Thread
# ==========================
listener_thread = threading.Thread(target=listen_for_command)
listener_thread.daemon = True
listener_thread.start()

# ==========================
# Play welcome message
# ==========================
speak_text("Welcome to Vector Robo!", lang="en")

# ==========================
# Main Loop (unchanged)
# ==========================
running = True
clock = pygame.time.Clock()
last_blink_time = time.time()
blink_duration = 0.1
is_blinking = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                load_image()
            elif event.key == pygame.K_c:
                capture_image_from_camera()

    current_time = time.time()

    if not is_blinking and current_time - last_blink_time > random.randint(3, 6):
        is_blinking = True
        blink_start_time = current_time
        last_blink_time = current_time
    if is_blinking and current_time - blink_start_time > blink_duration:
        is_blinking = False

    # Animate lip movement while speaking
    if speaking and time.time() - lip_last_switch > lip_switch_interval:
        lip_animation_state = not lip_animation_state
        lip_last_switch = time.time()

    draw_robot_head()
    draw_robot_body()
    draw_legs()
    draw_hand()
    draw_eyes(current_expression, is_blinking)
    draw_mouth(current_expression)
    draw_loaded_image(loaded_image_path)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
