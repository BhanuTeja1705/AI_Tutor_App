import streamlit as st
number = st.slider("Pick a number1", 0, 100)
st.write(number)
number2 = st.slider("Pick a number2", 0, 1000)
st.write(number2)
st.write(number+number2)