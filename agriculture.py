# ================== IMPORTS ==================
import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import io
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64

# ================== CONFIGURATION ==================
st.set_page_config(
    page_title="🌾 AI-Powered Agricultural Advisor",
    layout="wide"
)

GENAI_API_KEY = "AIzaSyDPAjI3VeKDVaQ_5LB61owH1uZJoiQjKiU"
WEATHER_API_KEY = "247d4ce6aa5e4ed6783c194649dd14a8"

# Initialize Gemini
genai.configure(api_key=GENAI_API_KEY)

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# ================== BACKGROUND IMAGE FUNCTION (URL BASED) ==================
def add_bg_from_url(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            encoded_string = base64.b64encode(response.content)
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{encoded_string.decode()}");
                    background-size: cover;
                    background-attachment: fixed;
                    color: #FFFFFF;
                }}
                .block-container {{
                    background-color: rgba(0, 0, 0, 0.65);
                    padding: 2rem;
                    border-radius: 15px;
                }}
                .stButton > button {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 0.75em 1.5em;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    transition: background-color 0.3s ease;
                }}
                .stButton > button:hover {{
                    background-color: #45a049;
                }}
                .stTextInput > div > input {{
                    background-color: rgba(255, 255, 255, 0.9);
                    color: black;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ Failed to load background image. Status Code:", response.status_code)
    except Exception as e:
        st.warning(f"⚠️ Error loading background image: {e}")

# ✅ Call the function with an ONLINE IMAGE URL
bg_image_url = "https://i.pinimg.com/736x/48/3b/4e/483b4eb7c2d89e7058e420eedf2dbf33.jpg"
add_bg_from_url(bg_image_url)

# ================== FUNCTIONS ==================
def get_weather(city):
    params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return f"Weather in {city}: {desc}, Temp: {temp}°C, Humidity: {humidity}%"
    else:
        return "⚠️ Unable to fetch weather data. Please check the city name."

def get_gemini_advice(prompt, model_name='gemini-1.5-pro-latest'):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"

def detect_disease_from_image(image_bytes):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content([
            {
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_bytes}},
                    {"text": "Analyze this crop image. Identify any plant disease, and suggest treatments and preventive measures in detail."}
                ]
            }
        ])
        return response.text
    except Exception as e:
        return f"❌ Vision Model Error: {e}"

def translate_text(text, dest_lang):
    try:
        translated = GoogleTranslator(source='auto', target=dest_lang).translate(text)
        return translated
    except Exception as e:
        return f"❌ Translation Error: {e}"

def recognize_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... Speak now!")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        detected_lang = 'auto'
        st.success(f"✅ Detected Language: {detected_lang.upper()}")
        return text, detected_lang
    except sr.UnknownValueError:
        return "❌ Could not understand audio", None
    except sr.RequestError as e:
        return f"❌ Could not request results; {e}", None

def text_to_speech(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        audio_bytes_io = io.BytesIO()
        tts.write_to_fp(audio_bytes_io)
        audio_bytes_io.seek(0)
        st.audio(audio_bytes_io, format='audio/mp3')
    except Exception as e:
        st.error(f"❌ TTS Error: {e}")

# ================== STREAMLIT UI ==================
st.title("🌾 AI-Powered Agricultural Advisor")
st.markdown("Get weather-based farming tips, diagnose crop diseases, and more using AI.")

# ================== TABS ==================
tabs = st.tabs([
    "🌦 Weather Advisory",
    "🖼 Disease Detection",
    "🏛 Govt Schemes",
    "🧪 Fertilizer & Soil Health",
    "🌐 Multilingual Text Support",
    "🎙 Voice Interaction"
])

languages = {
    'English': 'en',
    'Telugu': 'te',
    'Hindi': 'hi',
    'Tamil': 'ta',
    'Kannada': 'kn',
    'Malayalam': 'ml'
}

# ================== TAB 1: Weather-Based Advisory ==================
with tabs[0]:
    st.subheader("🌦 Weather-Based Farming Advice")
    selected_lang1 = st.selectbox("Choose Language for Advice", options=list(languages.keys()), key="lang_tab1")
    lang_code1 = languages[selected_lang1]
    city = st.text_input("Enter your City Name:", "Vijayawada")

    if st.button("Get Weather & Farming Advice"):
        with st.spinner("Fetching weather information..."):
            weather_info = get_weather(city)
            st.info(weather_info)

        prompt = f"""
        Act as an agricultural expert. Based on this weather data, provide detailed advice to farmers in {city} on:
        - Crop care
        - Irrigation strategies
        - Pest control measures
        - Fertilizer recommendations

        Weather Data: {weather_info}
        """
        with st.spinner("Generating farming advice..."):
            farming_advice = get_gemini_advice(prompt)
            translated_advice = translate_text(farming_advice, lang_code1)
            st.success("✅ Farming Advice Ready!")
            st.markdown(translated_advice)
            text_to_speech(translated_advice, lang=lang_code1)

# ================== TAB 2: Crop Disease Detection ==================
with tabs[1]:
    st.subheader("🖼 Crop Disease Detection & Treatment Suggestions")
    selected_lang2 = st.selectbox("Choose Language for Disease Report", options=list(languages.keys()), key="lang_tab2")
    lang_code2 = languages[selected_lang2]
    uploaded_file = st.file_uploader("Upload a Crop Leaf Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', width=300)

        if st.button("Detect Disease & Suggest Treatment"):
            with st.spinner("Analyzing image..."):
                image_bytes_io = io.BytesIO()
                image.save(image_bytes_io, format='JPEG')
                image_bytes = image_bytes_io.getvalue()

                result = detect_disease_from_image(image_bytes)
                translated_result = translate_text(result, lang_code2)

                st.success("✅ Analysis Complete!")
                st.markdown(translated_result)
                text_to_speech(translated_result, lang=lang_code2)

# ================== TAB 3: Latest Govt Schemes ==================
with tabs[2]:
    st.subheader("🏛 Government Schemes for Farmers")
    selected_lang3 = st.selectbox("Choose Language for Schemes", options=list(languages.keys()), key="lang_tab3")
    lang_code3 = languages[selected_lang3]

    if st.button("Get Latest Govt Schemes for Farmers"):
        prompt = """
        Act as an agricultural policy expert. Provide the latest government schemes for farmers in India,
        including subsidies, insurance, loan programs, and financial assistance for agricultural development.
        """
        with st.spinner("Fetching schemes..."):
            schemes_info = get_gemini_advice(prompt)
            translated_schemes = translate_text(schemes_info, lang_code3)
            st.success("✅ Schemes Information Ready!")
            st.markdown(translated_schemes)
            text_to_speech(translated_schemes, lang=lang_code3)

# ================== TAB 4: Fertilizer & Soil Health ==================
with tabs[3]:
    st.subheader("🧪 Fertilizer & Soil Health Recommendations")
    selected_lang4 = st.selectbox("Choose Language for Soil Health Advice", options=list(languages.keys()), key="lang_tab4")
    lang_code4 = languages[selected_lang4]
    crop = st.text_input("Enter Crop Name (e.g., Rice, Wheat):")

    if st.button("Get Fertilizer & Soil Health Advice"):
        prompt = f"""
        You are an expert agricultural consultant. Provide detailed fertilizer recommendations and soil health improvement tips 
        for growing {crop}. Include type of fertilizer, quantity, application schedule, and any organic practices if applicable.
        """
        with st.spinner("Generating recommendations..."):
            soil_advice = get_gemini_advice(prompt)
            translated_soil_advice = translate_text(soil_advice, lang_code4)
            st.success("✅ Fertilizer & Soil Health Advice Ready!")
            st.markdown(translated_soil_advice)
            text_to_speech(translated_soil_advice, lang=lang_code4)

# ================== TAB 5: Multilingual Text Support ==================
with tabs[4]:
    st.subheader("🌐 Multilingual Support - Translate Any Text")
    selected_lang5 = st.selectbox("Choose Language to Translate Into", options=list(languages.keys()), key="lang_tab5")
    lang_code5 = languages[selected_lang5]
    advice_text = st.text_area("Paste any text to translate it:")

    if st.button("Translate"):
        with st.spinner("Translating..."):
            translated_text = translate_text(advice_text, lang_code5)
            st.success("✅ Translation Ready!")
            st.markdown(translated_text)
            text_to_speech(translated_text, lang=lang_code5)

# ================== TAB 6: Multilingual Voice Interaction ==================
with tabs[5]:
    st.subheader("🎙 Multilingual Voice Interaction")
    output_lang6 = st.selectbox("Select Output Language", options=list(languages.keys()), key="lang_tab6")
    lang_code6 = languages[output_lang6]

    if st.button("🎤 Speak Now"):
        query, detected_lang = recognize_voice_input()

        if detected_lang:
            st.markdown(f"**You said:** `{query}`")
            query_in_english = translate_text(query, 'en')

            with st.spinner("Generating AI Response..."):
                ai_response = get_gemini_advice(query_in_english)
                final_response = translate_text(ai_response, lang_code6)

                st.success("✅ AI Response Ready!")
                st.markdown(f"**AI Response ({output_lang6}):** {final_response}")
                text_to_speech(final_response, lang=lang_code6)

# ================== FOOTER ==================
st.markdown("---")
st.caption("🚀 Built with Streamlit, OpenWeatherMap, Gemini 1.5 Pro, Deep Translator, SpeechRecognition, and gTTS | Created by Bhanuteja 🤍")
