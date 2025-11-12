import os
from dotenv import load_dotenv
import sqlite3
import streamlit as st
from PIL import Image
import google.generativeai as genai
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

DB_PATH = "company.db"

def run_sql_query(query: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()
        return columns, rows
    except Exception as e:
        return None, str(e)

st.set_page_config(page_title="Gemini SQL Assistant", page_icon="🧠")
st.title("Gemini SQL Assistant")
st.markdown("Ask a question about the database in natural language, and Gemini will generate and run an SQL query.")

user_question = st.text_input("Ask your question:", placeholder="e.g. What is the average salary in each department?")


if st.button("Run Query") and user_question:
    with st.spinner("Generating SQL query using Gemini..."):
        prompt = f"""
        You are an expert data analyst. The SQLite database has a table named 'employees' with columns:
        id, name, department, salary.
        Convert the following question into a correct SQL query for SQLite.

        Question: {user_question}

        Only return the SQL query, nothing else.
        """

        response = model.generate_content(prompt)
        sql_query = response.text.strip("`").strip()

    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")

    with st.spinner("Running SQL query..."):
        columns, result = run_sql_query(sql_query)

    if columns:
        st.subheader("Query Result")
        st.dataframe(result, use_container_width=True)
    else:
        st.error(f"Error executing query: {result}")