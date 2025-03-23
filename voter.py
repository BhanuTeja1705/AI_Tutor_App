import streamlit as st

# Set page configuration
st.set_page_config(page_title="Voter Registration Form", page_icon="🗳️", layout="centered")

st.title("🗳️ Voter Registration Form")

st.write("Please fill in the details below to register as a voter.")

# Create a form using st.form
with st.form("voter_registration_form"):
    # Basic Details
    full_name = st.text_input("Full Name")
    father_name = st.text_input("Father's/Mother's Name")
    gender = st.radio("Gender", ("Male", "Female", "Other"))
    dob = st.date_input("Date of Birth")
    age = st.number_input("Age", min_value=18, max_value=120, step=1)

    # Contact & Address
    address = st.text_area("Residential Address")
    state = st.selectbox("State", ("Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka", "Kerala", "Others"))
    district = st.text_input("District")
    pincode = st.text_input("Pincode")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address (Optional)")

    # Identity Information
    voter_id = st.text_input("Voter ID (if available)")
    aadhaar = st.text_input("Aadhaar Number (Optional)")

    # Upload Photo and Documents
    photo = st.file_uploader("Upload Passport Size Photo", type=["jpg", "jpeg", "png"])
    address_proof = st.file_uploader("Upload Address Proof Document", type=["pdf", "jpg", "jpeg", "png"])

    # Submit button
    submit = st.form_submit_button("Submit Registration")

# On submission
if submit:
    if full_name and father_name and age >= 18 and address and district and pincode and phone:
        st.success("✅ Registration Successful!")
        st.markdown("### 📝 Registration Details")
        st.write(f"**Full Name:** {full_name}")
        st.write(f"**Father's/Mother's Name:** {father_name}")
        st.write(f"**Gender:** {gender}")
        st.write(f"**Date of Birth:** {dob}")
        st.write(f"**Age:** {age}")
        st.write(f"**Address:** {address}, {district}, {state} - {pincode}")
        st.write(f"**Phone:** {phone}")
        if email:
            st.write(f"**Email:** {email}")
        if voter_id:
            st.write(f"**Voter ID:** {voter_id}")
        if aadhaar:
            st.write(f"**Aadhaar Number:** {aadhaar}")
        if photo:
            st.image(photo, width=150, caption="Uploaded Photo")
        if address_proof:
            st.write("Address Proof Document Uploaded Successfully!")
    else:
        st.error("❌ Please fill all required fields and ensure age is 18 or above.")
