import streamlit as st
from PIL import Image, ImageOps

# Set page title
st.set_page_config(page_title="Color to Black & White Converter", page_icon="🖼️")

st.title("🖼️ Color to Black & White Image Converter")
st.write("Upload your color photo, and we'll convert it into black and white! 📷➡️⚫⚪")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open the uploaded image
    image = Image.open(uploaded_file)

    # Convert to black and white
    bw_image = ImageOps.grayscale(image)

    # Create two columns side by side
    col1, col2 = st.columns(2)

    # Display original image in the first column
    with col1:
        st.subheader("Original Image")
        st.image(image, caption="Original", use_column_width=True)

    # Display black and white image in the second column
    with col2:
        st.subheader("Black & White Image")
        st.image(bw_image, caption="Black & White", use_column_width=True)

    # Download button under both images
    st.download_button(
        label="📥 Download Black & White Image",
        data=bw_image.tobytes(),
        file_name="black_and_white.png",
        mime="image/png"
    )
else:
    st.info("👆 Upload an image to get started.")
