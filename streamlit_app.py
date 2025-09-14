import streamlit as st
import requests
import json
import os
import subprocess
import threading
import time

API_ENDPOINT = "http://127.0.0.1:8000/ask_agent"
DATA_DIRECTORY = "data/documents"
CHROMA_PATH = "chroma"

os.makedirs(DATA_DIRECTORY, exist_ok=True)

# --- Functions ---
def run_ingestion_script(file_path):
    """Runs the document ingestion script."""
    try:
        result = subprocess.run(
            ["python", "process_documents.py", "--file", file_path],
            check=True,
            capture_output=True,
            text=True
        )
        st.success(f"Ingestion successful for {os.path.basename(file_path)}!")
        st.text(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Ingestion failed for {os.path.basename(file_path)}!")
        st.text(e.stderr)
        return False
    except FileNotFoundError:
        st.error("Error: 'process_documents.py' not found. Please ensure the file exists.")
        return False

def call_api(question, chat_history):
    """Sends a question to the FastAPI backend and gets a response."""
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"question": question, "chat_history": chat_history}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json().get("answer")
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the backend API: {e}")
        return "Sorry, I am unable to connect to the knowledge base right now."

def clear_chat_history():
    st.session_state.messages = []
    st.session_state.chat_history = ""
    st.session_state.ingestion_status = "pending"

st.set_page_config(page_title="Corporate Policy Navigator", layout="wide")
st.title("Corporate Policy and Knowledge Navigator")

with st.sidebar:
    st.header("Admin Controls")

    st.info("Upload your corporate policy PDFs here to build or expand the knowledge base.")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if 'ingestion_status' not in st.session_state:
        st.session_state.ingestion_status = "pending"

    if uploaded_files:
        if st.button("Process Documents"):
            st.session_state.ingestion_status = "processing"
            st.rerun()

    if st.session_state.ingestion_status == "processing":
        with st.spinner("Processing documents... This may take a few minutes."):
            all_successful = True
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATA_DIRECTORY, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                if not run_ingestion_script(file_path):
                    all_successful = False

            if all_successful:
                st.success("All documents processed successfully! You can now ask questions.")
            st.session_state.ingestion_status = "complete"
            st.rerun()

    st.button("Clear Chat History", on_click=clear_chat_history)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about company policies..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Searching and generating response..."):
        full_response = call_api(prompt, st.session_state.chat_history)

    st.session_state.chat_history += f"Human: {prompt}\nAI: {full_response}\n"

    with st.chat_message("assistant"):
        st.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})