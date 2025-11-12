import os
from dotenv import load_dotenv
import io
import streamlit as st
from PIL import Image
import json
import google.generativeai as genai
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

st.title("Food Image Analyzer")
st.markdown("Upload a food image to identify items, estimate calories, and get health recommendations using **Google Gemini Pro**.")

uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing image using Gemini..."):
    
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        prompt = (
            "You are a nutrition expert. Look at the image and identify all visible food items. "
            "For each item, provide:\n"
            "1. The name of the food\n"
            "2. Estimated calories for one serving (based on visual portion)\n"
            "3. A short recommendation (e.g., healthier alternatives or portion advice)\n\n"
            "Return your answer in JSON format like:\n"
            "[{'food': '...', 'approx_calories': '...', 'recommendation': '...'}, ...]"
        )

        try:
            response = model.generate_content(
                [prompt, {"mime_type": "image/png", "data": image_bytes.getvalue()}],
                generation_config={"temperature": 0.4},
            )
            result_text = response.text
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    st.subheader("Gemini’s Analysis")
    st.code(result_text, language="json")


    try:
        data = json.loads(result_text)
        st.subheader(" Breakdown")
        for item in data:
            st.markdown(
                f"**{item['food']}** — {item['approx_calories']} kcal  \n"
                f"_Recommendation:_ {item['recommendation']}"
            )
    except Exception:
        st.warning("Could not parse structured JSON. Displaying raw response instead.")
        st.write(result_text)

st.markdown("---")





