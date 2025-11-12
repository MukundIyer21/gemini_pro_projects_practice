import os
from dotenv import load_dotenv
import io
import streamlit as st
from PIL import Image
import google.generativeai as genai
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

st.title("Image Describer")
st.markdown("Upload an image, provide a prompt, and see what the Gemini model says.")

uploaded_file = st.file_uploader("Choose an image file (PNG/JPG)", type=["png","jpg","jpeg"])
prompt = st.text_area("Enter your prompt", height=100)

if uploaded_file is not None and prompt:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded image")

        image = Image.open(uploaded_file)

        with st.spinner("Calling Gemini API…"):
            answer = model.generate_content([image,prompt]).text

        st.subheader("Model’s response")
        st.write(answer)

    except Exception as e:
        st.error(f"Error: {e}")