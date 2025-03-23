import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pyttsx3
import speech_recognition as sr
import base64

# ============================
# FUNCTION: Set Background Image
# ============================
def set_bg_with_overlay(image_path):
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_data}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ============================
# FUNCTION: Custom CSS
# ============================
def apply_custom_styles():
    custom_css = """
    <style>
    .main-heading {
        font-size: 40px;
        color: #00FFFF;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    h2 {
        font-size: 24px !important;
        color: #deb887 !important;
        margin-top: 30px;
    }
    h1, h3, h4 {
        color: white !important;
    }
    p, div, span {
        color: #deb887 !important;
    }
    footer {
        visibility: hidden;
    }
    .footer-custom {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        color: #FFFFFF;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        z-index: 9999;
    }
    </style>

    <div class="footer-custom">
        Developed with ❤️ by Bhanuteja
    </div>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# ============================
# CONFIGURE STREAMLIT PAGE
# ============================
st.set_page_config(page_title="🤖 AI Powered Tutor", layout="wide")

# ============================
# APPLY BACKGROUND & CUSTOM STYLES
# ============================
set_bg_with_overlay('image/ai3.jpg')
apply_custom_styles()

# ============================
# CONFIGURE GEMINI API
# ============================
genai.configure(api_key='AIzaSyDPAjI3VeKDVaQ_5LB61owH1uZJoiQjKiU')  # Replace with your Gemini API Key

# ============================
# SESSION STATE INIT
# ============================
if "question_count" not in st.session_state:
    st.session_state.question_count = {"Mathematics": 0, "Physics": 0, "Chemistry": 0}
if "time_spent" not in st.session_state:
    st.session_state.time_spent = {"Mathematics": 0, "Physics": 0, "Chemistry": 0}
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# ============================
# LOGO + HEADING
# ============================
col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.image('image/ai_logo.png', width=100)

with col_title:
    st.markdown('<div class="main-heading">🤖 Welcome to AI Tutor</div>', unsafe_allow_html=True)

# ============================
# SIDEBAR INPUTS
# ============================
st.sidebar.header("📚 Choose your Learning Path")
grade = st.sidebar.selectbox("🎓 Select Grade/Level", list(range(1, 13)))
subject = st.sidebar.selectbox("📘 Choose Subject", ["Mathematics", "Physics", "Chemistry"])
language = st.sidebar.selectbox("🌐 Select Language", ["English", "Hindi", "Telugu"])

st.sidebar.markdown("🖼️ **Upload an image (optional)**")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type=["jpg", "jpeg", "png"])

# ============================
# VOICE INPUT FUNCTION
# ============================
def get_voice_input():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎙️ Listening... Please speak your question.")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"✅ You said: {text}")
            return text
    except sr.UnknownValueError:
        st.error("❗ Sorry, I couldn't understand your speech.")
    except sr.RequestError as e:
        st.error(f"❗ Speech Recognition error: {e}")
    except Exception as e:
        st.error(f"❗ Unexpected error: {e}")
    return ""

# ============================
# TRANSLATION FUNCTION
# ============================
def translate_text(answer, target_language):
    if target_language == "English":
        return answer
    translate_prompt = f"Translate the following answer into {target_language}:\n\n{answer}"
    try:
        translation_model = genai.GenerativeModel('gemini-1.5-pro-latest')
        translation_response = translation_model.generate_content(translate_prompt)
        return translation_response.text
    except Exception as e:
        st.error(f"Translation Error: {e}")
        return answer

# ============================
# TEXT TO SPEECH FUNCTION
# ============================
def speak_text_offline(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Offline TTS Error: {e}")

# ============================
# INPUT AREA FOR QUESTIONS
# ============================
st.header("✏️ Type your question or use voice input")

question_input = st.text_area("Ask your question here...", value=st.session_state.voice_input)

col_a, col_b = st.columns([1, 1])

with col_a:
    if st.button("🎤 Use Voice Input"):
        voice_text = get_voice_input()
        if voice_text:
            st.session_state.voice_input = voice_text
            st.rerun()

with col_b:
    submit_button = st.button("Submit")

# ============================
# RESPONSE GENERATION
# ============================
if submit_button and (question_input or uploaded_file):
    with st.spinner("🔎 Getting your answer..."):
        try:
            model = genai.GenerativeModel('gemini-1.5-pro-latest')

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

                image_bytes_io = io.BytesIO()
                image.save(image_bytes_io, format='PNG')
                image_bytes = image_bytes_io.getvalue()

                prompt_part_1 = f"You are an expert {subject} tutor for grade {grade}."
                prompt_part_2 = f"Explain this image along with this question: {question_input or 'Describe the content of the image in detail.'}"

                response = model.generate_content([
                    {"text": prompt_part_1},
                    {"text": prompt_part_2},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_bytes
                        }
                    }
                ])
            else:
                prompt = f"Grade {grade} {subject} question: {question_input}"
                response = model.generate_content(prompt)

            answer = response.text
            translated_answer = translate_text(answer, language)

            st.markdown(f"""
                <div style="background-color: rgba(0, 0, 0, 0.5); 
                            color: white; 
                            padding: 15px; 
                            border-radius: 10px;
                            font-size: 18px;">
                    📖 <b>Answer in {language}</b><br><br>
                    {translated_answer}
                </div>
            """, unsafe_allow_html=True)

            speak_text_offline(translated_answer)

            st.session_state.question_count[subject] += 1
            st.session_state.time_spent[subject] += 1

        except Exception as e:
            st.error(f"Error: {e}")

# ============================
# PROGRESS OVERVIEW SECTION
# ============================
st.markdown("<h2>📊 Progress Overview</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

def subject_card(subject, emoji, color, total_questions=10):
    count = st.session_state.question_count[subject]
    time_spent = st.session_state.time_spent[subject]

    progress_percent = min(int((count / total_questions) * 100), 100)

    with st.container():
        st.markdown(f"""
            <div style="background-color:#1E293B; padding:10px; border-radius:10px; width:250px;">
                <h3 style="color:white; font-size:20px;"><span style="font-size:22px;">{emoji}</span> {subject}</h3>
                <p style="color:white; font-size:14px;">📝 <b>{count}</b> Questions Answered</p>
                <p style="color:white; font-size:14px;">⏱️ <b>{time_spent}</b> min Spent</p>
                <div style="background-color:#374151; border-radius:20px; height:15px; overflow: hidden;">
                    <div style="
                        height:100%;
                        width:{progress_percent}% ;
                        background: linear-gradient(90deg, {color});
                        border-radius:20px;
                        transition: width 1s ease;">
                    </div>
                </div>
                <p style="color:white; font-size:12px; margin-top:5px;">{progress_percent}% Complete</p>
            </div>
        """, unsafe_allow_html=True)

with col1:
    subject_card("Mathematics", "📐", "#10B981, #3B82F6")

with col2:
    subject_card("Physics", "🔬", "#F59E0B, #EF4444")

with col3:
    subject_card("Chemistry", "🧪", "#6366F1, #EC4899")
