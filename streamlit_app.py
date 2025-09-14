import streamlit as st
import requests
import os
import subprocess
import json
import time

# --- Import Utility Functions ---
from utils.file_handlers import save_uploaded_file
from utils.citation_formatter import format_citations
from utils.auth_service import get_allowed_documents

# --- Configuration ---
API_ENDPOINT = "http://127.0.0.1:8000/ask_agent"
DATA_DIRECTORY = "data/documents"
CHROMA_PATH = "chroma"

# Ensure data directory exists
os.makedirs(DATA_DIRECTORY, exist_ok=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
if "current_role" not in st.session_state:
    st.session_state.current_role = "Employee"
if "ingestion_status" not in st.session_state:
    st.session_state.ingestion_status = "pending"

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

def call_api(question, chat_history, role):
    """Sends a question to the FastAPI backend with role context."""
    try:
        response = requests.post(
            API_ENDPOINT,
            json={
                "question": question,
                "chat_history": chat_history,
                "role": role
            }
        )
        response.raise_for_status()
        return response.json().get("answer")
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the backend API: {e}")
        return "Sorry, I am unable to connect to the knowledge base right now."

def clear_chat_history():
    st.session_state.messages = []
    st.session_state.chat_history = ""
    st.session_state.ingestion_status = "pending"

# --- Streamlit UI ---
st.set_page_config(page_title="Corporate Knowledge Navigator", layout="wide")
st.title("🤖 Corporate Policy and Knowledge Navigator")

# Sidebar for file upload, role selection, and controls
with st.sidebar:
    st.header("Admin & User Controls")

    st.info("Upload your corporate policy PDFs here to build or expand the knowledge base.")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

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
            st.rerun() # Corrected from st.experimental_rerun()

    st.button("Clear Chat History", on_click=clear_chat_history)

    st.divider()
    st.subheader("User Role Simulation")
    role_options = ["Employee", "HR_Manager", "IT_Admin"]
    selected_role = st.selectbox(
        "Select your role:",
        options=role_options,
        index=role_options.index(st.session_state.current_role)
    )
    if selected_role != st.session_state.current_role:
        st.session_state.current_role = selected_role
        st.session_state.messages = []
        st.session_state.chat_history = ""
        st.rerun() # Corrected from st.experimental_rerun()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about company policies..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Searching and generating response..."):
        full_response = call_api(prompt, st.session_state.chat_history, st.session_state.current_role)

    st.session_state.chat_history += f"Human: {prompt}\nAI: {full_response}\n"

    with st.chat_message("assistant"):
        st.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})