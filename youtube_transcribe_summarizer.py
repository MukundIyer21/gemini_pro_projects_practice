import os
from dotenv import load_dotenv
import io
import streamlit as st
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import json
import google.generativeai as genai
import re
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

def extract_video_id(url: str):
    """
    Extracts the YouTube video ID from any YouTube URL format.
    """
    regex = (
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([A-Za-z0-9_-]{11})"
    )
    match = re.match(regex, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id: str):
    """
    Fetch transcript text using YouTubeTranscriptApi.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        text = " ".join([t["text"] for t in transcript])
        return text
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

def summarize_text(text: str):
    """
    Summarizes long transcripts by chunking them and then asking Gemini for a combined summary.
    """
    CHUNK_SIZE = 8000
    chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    summaries = []

    for i, chunk in enumerate(chunks):
        prompt = f"Summarize this part of a YouTube transcript (part {i+1}):\n\n{chunk}"
        response = model.generate_content(prompt, generation_config={"temperature": 0.5})
        summaries.append(response.text)

    combined_prompt = (
        "Combine and refine the following partial summaries into a single coherent summary "
        "that captures the main points, key details, and tone of the original video:\n\n"
        + "\n\n".join(summaries)
    )
    final_response = model.generate_content(combined_prompt, generation_config={"temperature": 0.4})
    return final_response.text


st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
st.title("YouTube Video Summarizer")
st.write("Enter a YouTube URL and get a concise summary of the video transcript using **Google Gemini Pro**.")

url = st.text_input("Enter YouTube URL")

if url:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL. Please enter a proper link.")
    else:
        with st.spinner("Fetching transcript..."):
            transcript = get_youtube_transcript(video_id)

        if not transcript:
            st.error("Transcript not found or unavailable for this video.")
        else:
            st.success("Transcript retrieved successfully!")
            with st.expander("View full transcript"):
                st.write(transcript[:5000] + ("..." if len(transcript) > 5000 else ""))

            with st.spinner("Summarizing using Gemini..."):
                summary = summarize_text(transcript)

            st.subheader("Video Summary")
            st.write(summary)

st.markdown("---")