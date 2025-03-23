import streamlit as st
from openai import OpenAI

# --- Initialize the OpenAI client ---
client = OpenAI(api_key="AIzaSyCjxdgf-ioqlY04pJSkoZFSz66DHuGD6KU")  # Replace with your actual key!

# --- Streamlit Page Setup ---
st.set_page_config(page_title="ChatGPT Clone", page_icon="🤖")
st.title("🤖 ChatGPT Clone with Streamlit (OpenAI v1.x)")

# --- Chat History Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant!"}
    ]

# --- Display chat history ---
for chat in st.session_state.messages[1:]:  # Skip system message
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# --- User input ---
prompt = st.chat_input("Type your message...")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenAI ChatCompletion using v1.0+ API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use gpt-4 if you have access
            messages=st.session_state.messages
        )

        full_response = response.choices[0].message.content.strip()

        # Display assistant message in chat
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
