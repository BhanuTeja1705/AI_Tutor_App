import streamlit as st

# Set page config
st.set_page_config(page_title="Streamlit Calculator", page_icon="🧮", layout="centered")

st.title("🧮 Simple Calculator")

# Initialize session state for expression if not already set
if "expression" not in st.session_state:
    st.session_state.expression = ""

# Function to update the expression when a button is pressed
def press_button(label):
    st.session_state.expression += str(label)

# Function to clear the expression
def clear():
    st.session_state.expression = ""

# Function to evaluate the expression
def calculate():
    try:
        result = str(eval(st.session_state.expression))
        st.session_state.expression = result
    except Exception:
        st.session_state.expression = "Error"

# Display the current expression
st.text_input("Expression", st.session_state.expression, disabled=True)

# Calculator layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

# Create the button grid
for row in buttons:
    cols = st.columns(4)
    for idx, label in enumerate(row):
        if label == "=":
            cols[idx].button(label, on_click=calculate)
        else:
            cols[idx].button(label, on_click=press_button, args=(label,))

# Clear button
st.button("Clear", on_click=clear)
