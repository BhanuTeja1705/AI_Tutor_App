import streamlit as st
import requests
import google.generativeai as genai
from PIL import Image
import io

# ================== CONFIGURATION ==================
GENAI_API_KEY = "AIzaSyC9jghMMw2dt94DQ5t-_mNyUfeDnck9DwY"  # ✅ Replace with your Gemini API Key
WEATHER_API_KEY = "247d4ce6aa5e4ed6783c194649dd14a8"  # ✅ Replace with your OpenWeatherMap API Key

# Initialize Gemini
genai.configure(api_key=GENAI_API_KEY)

# Weather API Endpoint
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


# ================== FUNCTIONS ==================

def get_weather(city):
    """Fetch weather data for a given city using OpenWeatherMap API."""
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
    """Generate text-based advice from Gemini 1.5 Pro."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"


def detect_disease_from_image(image_bytes):
    """
    Analyze an uploaded crop image and detect any disease using Gemini 1.5 Pro.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(
            [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",  # or 'image/png' if needed
                                "data": image_bytes
                            }
                        },
                        {
                            "text": "Analyze this crop image. Identify any plant disease, and suggest treatments and preventive measures in detail."
                        }
                    ]
                }
            ]
        )
        return response.text
    except Exception as e:
        return f"❌ Vision Model Error: {e}"


def translate_to_telugu(text):
    """Translate any text to Telugu."""
    prompt = f"Translate the following text to Telugu:\n\n{text}"
    return get_gemini_advice(prompt)


# ================== STREAMLIT UI ==================

st.set_page_config(page_title="🌾 AI-Powered Agricultural Advisor", layout="wide")
st.title("🌾 AI-Powered Agricultural Advisor")
st.markdown("Get weather-based farming tips, diagnose crop diseases, and more using AI.")

# Tabs
tabs = st.tabs(["🌦 Weather Advisory", "🖼 Disease Detection", "🏛 Govt Schemes", "🧪 Fertilizer & Soil Health",
                "🌐 Multilingual Support"])

# ================== TAB 1: Weather-Based Advisory ==================
with tabs[0]:
    st.subheader("🌦 Weather-Based Farming Advice")

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
            st.success("✅ Farming Advice Ready!")
            st.markdown(farming_advice)

# ================== TAB 2: Crop Disease Detection ==================
with tabs[1]:
    st.subheader("🖼 Crop Disease Detection & Treatment Suggestions")

    uploaded_file = st.file_uploader("Upload a Crop Leaf Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', width=300)

        if st.button("Detect Disease & Suggest Treatment"):
            with st.spinner("Analyzing image..."):
                # Convert image to bytes
                image_bytes_io = io.BytesIO()
                image.save(image_bytes_io, format='JPEG')  # Change to 'PNG' if needed
                image_bytes = image_bytes_io.getvalue()

                # Detect disease
                result = detect_disease_from_image(image_bytes)
                st.success("✅ Analysis Complete!")
                st.markdown(result)

# ================== TAB 3: Latest Govt Schemes ==================
with tabs[2]:
    st.subheader("🏛 Government Schemes for Farmers")

    if st.button("Get Latest Govt Schemes for Farmers"):
        prompt = """
        Act as an agricultural policy expert. Provide the latest government schemes for farmers in India,
        including subsidies, insurance, loan programs, and financial assistance for agricultural development.
        """
        with st.spinner("Fetching schemes..."):
            schemes_info = get_gemini_advice(prompt)
            st.success("✅ Schemes Information Ready!")
            st.markdown(schemes_info)

# ================== TAB 4: Fertilizer & Soil Health ==================
with tabs[3]:
    st.subheader("🧪 Fertilizer & Soil Health Recommendations")

    crop = st.text_input("Enter Crop Name (e.g., Rice, Wheat):")

    if st.button("Get Fertilizer & Soil Health Advice"):
        prompt = f"""
        You are an expert agricultural consultant. Provide detailed fertilizer recommendations and soil health improvement tips 
        for growing {crop}. Include type of fertilizer, quantity, application schedule, and any organic practices if applicable.
        """
        with st.spinner("Generating recommendations..."):
            soil_advice = get_gemini_advice(prompt)
            st.success("✅ Fertilizer & Soil Health Advice Ready!")
            st.markdown(soil_advice)

# ================== TAB 5: Multilingual Support ==================
with tabs[4]:
    st.subheader("🌐 Multilingual Support - Translate to Telugu")

    advice_text = st.text_area("Paste any text to translate it into Telugu:")

    if st.button("Translate to Telugu"):
        with st.spinner("Translating..."):
            translated_text = translate_to_telugu(advice_text)
            st.success("✅ Translation Ready!")
            st.markdown(translated_text)

# ================== FOOTER ==================
st.markdown("---")
st.caption("🚀 Built with Streamlit, OpenWeatherMap, and Gemini 1.5 Pro Model. | Created by Bhanuteja")
