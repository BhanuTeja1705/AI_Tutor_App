import streamlit as st
import google.generativeai as genai

# Set page config
st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🤖")

# Gemini API key (keep this private in real use)
genai.configure(api_key="AIzaSyD16s4bk-t0_97MU586C4X0WdIRUAnuuWM")

# Create the Gemini model instance
model = genai.GenerativeModel("gemini-pro")

# Streamlit UI
st.title("🤖 Gemini AI Chatbot")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat history display
for message in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(message["user"])
    with st.chat_message("assistant"):
        st.markdown(message["bot"])

# User input box
user_input = st.chat_input("Ask Gemini AI anything...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.spinner("Gemini AI is thinking..."):
        try:
            response = model.generate_content(user_input)
            ai_reply = response.text
        except Exception as e:
            ai_reply = f"Error: {str(e)}"

    # Show AI response
    with st.chat_message("assistant"):
        st.markdown(ai_reply)

    # Save to history
    st.session_state.chat_history.append({"user": user_input, "bot": ai_reply})
