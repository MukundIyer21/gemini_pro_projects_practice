import os
from dotenv import load_dotenv
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.document_loaders import PyPDFLoader
import streamlit as st
from langchain_classic.chains import conversational_retrieval
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.vectorstores import FAISS
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Document Q&A with Gemini + Groq", page_icon="📚")
st.title("Ask Questions About Your Document")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
if uploaded_file is not None:
    with st.spinner("Loading and processing your document..."):
        
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        loader = PyPDFLoader("temp.pdf")
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(documents)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_documents(chunks, embedding=embeddings)

        retriever = vector_store.as_retriever(search_kwargs={"k": 4})

        qa_chain = conversational_retrieval.from_llm(
            llm=model,
            retriever=retriever,
            return_source_documents=True
        )

    st.success("Document processed! You can now ask questions below.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    question = st.text_input("Ask a question about the document:")

    if question:
        with st.spinner("Thinking..."):
            result = qa_chain({"question": question, "chat_history": st.session_state.chat_history})
            st.session_state.chat_history.append((question, result["answer"]))

        st.markdown("### Answer:")
        st.write(result["answer"])

        with st.expander("Show retrieved context"):
            for doc in result["source_documents"]:
                st.write(doc.page_content[:500] + "...")


