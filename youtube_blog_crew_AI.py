import streamlit as st
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
load_dotenv()
class ToolResult:
    def __init__(self, ok, output=None, error=None):
        self.ok = ok
        self.output = output
        self.error = error

class YouTubeTranscriptTool:
    def run(self, video_url):

        video_id = self.extract_id(video_url)
        if not video_id:
            return ToolResult(False, error="Invalid YouTube URL or ID")

        try:
            data = YouTubeTranscriptApi.get_transcript(video_id)
            text = "\n".join([seg['text'] for seg in data])
            return ToolResult(True, text)
        except Exception as e:
            return ToolResult(False, error=str(e))

    def extract_id(self, url):
        match = re.search(r'(?:v=|\/)([A-Za-z0-9_-]{11})', url)
        return match.group(1) if match else None

class LLMTool:
    def __init__(self, model="gpt-4o-mini", api_key=None):
        import openai
        self.openai = openai
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def run(self, prompt):
        if not self.api_key:
            return ToolResult(False, error="Missing OPENAI_API_KEY")
        try:
            self.openai.api_key = self.api_key
            response = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "system", "content": "Write an engaging blog post."}, {"role": "user", "content": prompt}],
            )
            text = response["choices"][0]["message"]["content"]
            return ToolResult(True, text)
        except Exception as e:
            return ToolResult(False, error=str(e))
        
        
class TranscriptAgent:
    def __init__(self, tool):
        self.tool = tool

    def run(self, url):
        return self.tool.run(url)

class BlogWriterAgent:
    def __init__(self, tool):
        self.tool = tool

    def run(self, transcript):
        prompt = f"Create a blog post summarizing the following transcript:\n{transcript}\nMake it engaging, clear, and well-structured."
        return self.tool.run(prompt)

st.set_page_config(page_title="YouTube to Blog", layout="centered")
st.title("YouTube → Blog Generator")

url = st.text_input("Enter YouTube URL:")
model = st.selectbox("Choose Model", ["gpt-4o-mini", "gpt-4o"])

if st.button("Generate Blog"):
    if not url:
        st.error("Please enter a YouTube URL.")
    else:
        st.info("Fetching transcript...")
        transcript_tool = YouTubeTranscriptTool()
        llm_tool = LLMTool(model=model)
        transcript_agent = TranscriptAgent(transcript_tool)
        blog_agent = BlogWriterAgent(llm_tool)

        t_result = transcript_agent.run(url)
        if not t_result.ok:
            st.error(f"Transcript error: {t_result.error}")
        else:
            st.success("Transcript fetched.")
            st.text_area("Transcript (first 1000 chars)", t_result.output[:1000], height=150)

            st.info("Generating blog...")
            w_result = blog_agent.run(t_result.output)
            if not w_result.ok:
                st.error(f"Blog generation failed: {w_result.error}")
            else:
                st.success("Blog generated!")
                st.markdown(w_result.output)
                st.download_button("Download Blog", w_result.output, file_name="blog.md", mime="text/markdown")
