
import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Tools
class ToolResult:
    def __init__(self, ok, output=None, error=None):
        self.ok = ok
        self.output = output
        self.error = error

class NewsSearchTool:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.endpoint = "https://newsapi.org/v2/everything"

    def run(self, topic, language="en", max_articles=5):
        if not self.api_key:
            return ToolResult(False, error="Missing NEWS_API_KEY.")
        params = {
            "q": topic,
            "sortBy": "publishedAt",
            "language": language,
            "pageSize": max_articles,
            "apiKey": self.api_key,
        }
        try:
            r = requests.get(self.endpoint, params=params)
            data = r.json()
            if data.get("status") != "ok":
                return ToolResult(False, error=data.get("message", "Unknown error"))

            articles = data.get("articles", [])
            if not articles:
                return ToolResult(False, error="No articles found.")

            summaries = []
            for a in articles:
                summaries.append(f"Title: {a['title']}\nSource: {a['source']['name']}\nURL: {a['url']}\nDescription: {a['description']}\n")
            return ToolResult(True, "\n\n".join(summaries))
        except Exception as e:
            return ToolResult(False, error=str(e))

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
                messages=[{"role": "system", "content": "You are a professional journalist who writes concise news reports."}, {"role": "user", "content": prompt}],
            )
            text = response["choices"][0]["message"]["content"]
            return ToolResult(True, text)
        except Exception as e:
            return ToolResult(False, error=str(e))

# Agents
class NewsResearchAgent:
    def __init__(self, tool):
        self.tool = tool

    def run(self, topic):
        return self.tool.run(topic)

class NewsWriterAgent:
    def __init__(self, tool):
        self.tool = tool

    def run(self, news_data, topic):
        prompt = f"Write a detailed, structured news report about '{topic}' based on the following articles:\n{news_data}\n\nFormat the report with a title, summary, and analysis section."
        return self.tool.run(prompt)

# Streamlit UI
st.set_page_config(page_title="AI News Reporter", layout="centered")
st.title("Crew-AI News Reporter")

st.write("Enter a topic and let AI research and report the latest news!")

topic = st.text_input("Enter a topic (e.g., AI, climate change, Bitcoin)")
model = st.selectbox("Choose Model", ["gpt-4o-mini", "gpt-4o"])

if st.button("Generate News Report"):
    if not topic:
        st.error("Please enter a topic.")
    else:
        st.info("Researching recent news...")
        news_tool = NewsSearchTool()
        llm_tool = LLMTool(model=model)

        research_agent = NewsResearchAgent(news_tool)
        writer_agent = NewsWriterAgent(llm_tool)

        research_result = research_agent.run(topic)
        if not research_result.ok:
            st.error(f"Research failed: {research_result.error}")
        else:
            st.success("News research complete.")
            st.text_area("Recent Articles (summaries)", research_result.output[:2000], height=250)

            st.info("Writing report...")
            report_result = writer_agent.run(research_result.output, topic)
            if not report_result.ok:
                st.error(f"Report generation failed: {report_result.error}")
            else:
                st.success("Report generated!")
                st.markdown(report_result.output)
                st.download_button("Download Report", report_result.output, file_name="news_report.md", mime="text/markdown")