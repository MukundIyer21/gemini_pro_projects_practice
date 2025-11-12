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

st.set_page_config(page_title="Gemini Q&A Chatbot")
st.title("Gemini Q&A Chatbot")
st.markdown("Ask any question — the chatbot will respond using Google's Gemini model.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
user_input = st.chat_input("Type your question here...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "text": user_input})

    with st.spinner("Gemini is thinking..."):
        chat = model.start_chat(history=[
            {"role": msg["role"], "parts": [msg["text"]]} for msg in st.session_state.chat_history
        ])
        response = chat.send_message(user_input)
        answer = response.text
    st.session_state.chat_history.append({"role": "model", "text": answer})

for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["text"])
    else:
        st.chat_message("assistant").markdown(message["text"])