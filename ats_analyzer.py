import os
from dotenv import load_dotenv
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.document_loaders import PyPDFLoader
import streamlit as st
from langchain_classic.chains import conversational_retrieval
import google.generativeai as genai
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.vectorstores import FAISS
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Resume Analyzer")
st.title("AI Resume Analyzer (Powered by Gemini)")

def extract_text_from_pdf(uploaded_file):
    """Extracts text from uploaded PDF"""
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def get_gemini_response(prompt):
    """Helper to get Gemini model response"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"
    
uploaded_resume = st.file_uploader("Upload your Resume (PDF/TXT)", type=["pdf", "txt"])
job_description = st.text_area("Paste Job Description (optional)", placeholder="e.g. Data Scientist at XYZ...")

if uploaded_resume:
    if uploaded_resume.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_resume)
    else:
        resume_text = uploaded_resume.read().decode("utf-8")

    st.success("Resume uploaded and processed successfully!")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        match_btn = st.button("Match %")
    with col2:
        summary_btn = st.button("Summarize")
    with col3:
        keywords_btn = st.button("Missing Keywords")
    with col4:
        improve_btn = st.button("Suggestions")

    if match_btn:
        if not job_description:
            st.warning("Please paste a job description to calculate match %.")
        else:
            with st.spinner("Calculating match percentage..."):
                prompt = f"""
                Compare the following resume and job description.
                Return only the percentage match (0–100%) with one short justification.

                Resume:
                {resume_text[:6000]}

                Job Description:
                {job_description}
                """
                answer = get_gemini_response(prompt)
            st.subheader("Match Percentage")
            st.write(answer)

    elif summary_btn:
        with st.spinner("Summarizing resume..."):
            prompt = f"""
            Summarize the following resume in concise bullet points highlighting key skills, experience, and achievements.

            Resume:
            {resume_text[:6000]}
            """
            answer = get_gemini_response(prompt)
        st.subheader("Resume Summary")
        st.write(answer)

    elif keywords_btn:
        if not job_description:
            st.warning("Please paste a job description to find missing keywords.")
        else:
            with st.spinner("Finding missing keywords..."):
                prompt = f"""
                Compare the resume and job description.
                List important keywords and skills mentioned in the job description but missing from the resume.

                Resume:
                {resume_text[:6000]}

                Job Description:
                {job_description}
                """
                answer = get_gemini_response(prompt)
            st.subheader("Missing Keywords")
            st.write(answer)

    elif improve_btn:
        with st.spinner("Generating improvement suggestions..."):
            prompt = f"""
            Review the following resume.
            Provide suggestions to improve it — focus on structure, language, measurable results, and formatting.

            Resume:
            {resume_text[:6000]}
            """
            answer = get_gemini_response(prompt)
        st.subheader("Resume Improvement Suggestions")
        st.write(answer)
else:
    st.info("👆 Please upload your resume to get started.")
